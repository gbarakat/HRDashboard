"""Learner segments: k-means on elective training behaviour over the last 24 months.

Features: share of elective hours in five categories (the learning "mix") plus log(1 + elective
hours) (the intensity), standardised. k is the smallest value in 3..7 whose silhouette is within
0.03 of the best (parsimony rule); segments are named from their centroid profile.
Writes ml.training_segments.
Recovery check: agreement with the generator's planted learner archetypes (adjusted Rand index).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from ml import SEED, banner, read, write

FEATURES = {
    "elective_technical_hours": "Technical",
    "elective_leadership_hours": "Leadership",
    "elective_digital_hours": "Digital",
    "elective_customer_hours": "Customer Service",
    "elective_safety_hours": "Safety & Compliance",
}
LABELS = {"Technical": "Technical deep-diver", "Leadership": "Leadership track", "Digital": "Digital upskiller",
          "Customer Service": "Service focused", "Safety & Compliance": "Compliance only"}
MIN_ARI = 0.60
SILHOUETTE_SLACK = 0.03


def label_segments(profile: pd.DataFrame) -> dict[int, str]:
    """Name each cluster from its mean elective hours (original units)."""
    names = {}
    for seg, row in profile.iterrows():
        total = row[list(FEATURES)].sum()
        name = "Minimal engagement" if total < 1.0 else LABELS[FEATURES[row[list(FEATURES)].astype(float).idxmax()]]
        taken = sum(1 for v in names.values() if v.split(" (")[0] == name)
        names[seg] = f"{name} ({taken + 1})" if taken else name
    return names


def feature_matrix(df: pd.DataFrame) -> np.ndarray:
    hours = df[list(FEATURES)].astype(float)
    total = hours.sum(axis=1)
    shares = hours.div(total.where(total > 0, 1.0), axis=0)
    return StandardScaler().fit_transform(np.column_stack([shares.to_numpy(), np.log1p(total.to_numpy())]))


def fit(df: pd.DataFrame) -> tuple[np.ndarray, int, dict[int, float]]:
    x = feature_matrix(df)
    scores, fits = {}, {}
    for k in range(3, 8):
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(x)
        scores[k] = silhouette_score(x, km.labels_, sample_size=min(len(x), 3000), random_state=SEED)
        fits[k] = km.labels_
    best = min(k for k, v in scores.items() if v >= max(scores.values()) - SILHOUETTE_SLACK)
    return fits[best], best, scores


def planted_archetypes(emp_ids: pd.Series) -> pd.Series:
    """Ground truth from the (deterministic) generator - used only to prove recovery, never as a feature."""
    from generator import load_config
    from generator.population import build_roster
    roster = build_roster(load_config())["roster"].set_index("emp_id")
    return roster.loc[emp_ids, "learner_archetype"].reset_index(drop=True)


def main() -> dict:
    df = read("select * from ml.feat_learner_profile order by emp_id").reset_index(drop=True)
    labels, k, scores = fit(df)
    df["segment"] = labels + 1
    profile = df.groupby("segment")[list(FEATURES)].mean()
    names = label_segments(profile)
    df["segment_label"] = df["segment"].map(names)
    out = df[["employee_key", "emp_id", "org_unit_key", "segment", "segment_label", "total_hours",
              "elective_courses", *FEATURES]].copy()
    out["silhouette"] = round(scores[k], 4)
    write(out, "training_segments")

    ari = adjusted_rand_score(planted_archetypes(df["emp_id"]), df["segment_label"])
    banner(f"Learner segments (n={len(df)})")
    print("silhouette by k: " + ", ".join(f"k={kk}: {v:.3f}" for kk, v in scores.items()) + f"  -> k={k}")
    summary = df.groupby("segment_label").agg(employees=("emp_id", "size"), avg_hours_24m=("total_hours", "mean"))
    print(summary.round(1).to_string())
    ok = ari >= MIN_ARI
    print(f"agreement with planted archetypes: ARI = {ari:.2f} (>= {MIN_ARI})  ->  {'RECOVERED' if ok else 'NOT RECOVERED'}")
    return {"k": k, "ari": ari, "recovered": ok}


if __name__ == "__main__":
    main()
