"""Voluntary attrition: logistic regression on 31-Dec snapshots (outcome = voluntary exit in 12 months).

Design
  * unit: employee x snapshot (2018-12-31 .. 2024-12-31 labelled; 2025-12-31 scored only)
  * 70/30 split BY EMPLOYEE, stratified on "ever left voluntarily", seed 42 - no person is in both sets
  * statsmodels Logit with cluster-robust (employee) standard errors for coefficients / odds ratios
  * AUC and ROC on the held-out 30%
Writes ml.attrition_scores, ml.attrition_coefficients, ml.attrition_roc, ml.attrition_metrics.
Coefficients are associations, not causal effects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

from ml import CONFIG, SEED, banner, read, write

TENURE_BANDS = ["0-6m", "6-12m", "1-2y", "5-10y", "10y+"]          # reference: 2-5y
RATING_BANDS = ["low", "high", "none"]                              # reference: mid (rating 3)
PLANTED = {
    "commute_over_30km": CONFIG["attrition"]["planted_odds_ratio_commute_gt_30km"],
    "training_over_20h": CONFIG["attrition"]["planted_odds_ratio_training_gt_20h"],
}
OR_TOLERANCE = 0.25


def design(df: pd.DataFrame) -> pd.DataFrame:
    x = pd.DataFrame(index=df.index)
    x["commute_over_30km"] = (df["commute_km"].astype(float) > 30).astype(float)
    x["training_over_20h"] = (df["training_hours_12m"].astype(float) > 20).astype(float)
    x["age_under_30"] = (df["age_years"] < 30).astype(float)
    x["is_female"] = (df["gender"] == "Female").astype(float)
    for b in TENURE_BANDS:
        x[f"tenure_{b}"] = (df["tenure_band"] == b).astype(float)
    for b in RATING_BANDS:
        x[f"rating_{b}"] = (df["rating_band"] == b).astype(float)
    x["grade_G5_G8"] = (df["grade_band"] == "G5-G8").astype(float)
    x["grade_G9_G12"] = (df["grade_band"] == "G9-G12").astype(float)
    return sm.add_constant(x)


def split_by_employee(labelled: pd.DataFrame) -> pd.Series:
    ever = labelled.groupby("emp_id")["left_voluntary_12m"].max()
    train_ids, _ = train_test_split(ever.index, test_size=0.30, stratify=ever.values, random_state=SEED)
    return labelled["emp_id"].isin(set(train_ids)).map({True: "train", False: "test"})


def main() -> dict:
    snap = read("select * from ml.feat_attrition_snapshot order by snapshot_date, emp_id").reset_index(drop=True)
    labelled = snap[snap["left_voluntary_12m"].notna()].copy()
    labelled["left_voluntary_12m"] = labelled["left_voluntary_12m"].astype(int)
    labelled["split"] = split_by_employee(labelled)
    train, test = labelled[labelled["split"] == "train"], labelled[labelled["split"] == "test"]

    xtr, ytr = design(train), train["left_voluntary_12m"]
    model = sm.Logit(ytr, xtr).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(train["emp_id"])[0]})

    # ---- coefficients
    ci = model.conf_int()
    coefs = pd.DataFrame({
        "variable": model.params.index, "coef": model.params.values, "std_err": model.bse.values,
        "odds_ratio": np.exp(model.params.values), "or_ci_low": np.exp(ci[0].values),
        "or_ci_high": np.exp(ci[1].values), "p_value": model.pvalues.values})
    coefs["planted_odds_ratio"] = coefs["variable"].map(PLANTED)

    # ---- held-out performance
    p_test = model.predict(design(test))
    auc = roc_auc_score(test["left_voluntary_12m"], p_test)
    fpr, tpr, thr = roc_curve(test["left_voluntary_12m"], p_test)
    roc = pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": np.minimum(thr, 1.0)})

    # ---- scores for every snapshot (train, test, and the unlabelled current one)
    snap["p_leave"] = model.predict(design(snap))
    snap["split"] = "current"
    snap.loc[labelled.index, "split"] = labelled["split"]
    snap["decile"] = snap.groupby("snapshot_date")["p_leave"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 10, labels=False) + 1).astype(int)
    scores = snap[["employee_key", "emp_id", "org_unit_key", "snapshot_date", "p_leave", "decile", "split",
                   "left_voluntary_12m"]].rename(columns={"left_voluntary_12m": "left_within_12m"})
    scores["p_leave"] = scores["p_leave"].round(6)

    base_rate = test["left_voluntary_12m"].mean()
    metrics = pd.DataFrame([
        ("auc_test", auc), ("brier_test", brier_score_loss(test["left_voluntary_12m"], p_test)),
        ("base_rate_test", base_rate), ("n_train", len(train)), ("n_test", len(test)),
        ("events_train", int(ytr.sum())), ("events_test", int(test["left_voluntary_12m"].sum())),
        ("employees_train", train["emp_id"].nunique()), ("employees_test", test["emp_id"].nunique()),
        ("pseudo_r2_train", model.prsquared), ("snapshots_scored_current", int((snap["split"] == "current").sum())),
    ], columns=["metric", "value"])

    write(scores, "attrition_scores")
    write(coefs, "attrition_coefficients")
    write(roc, "attrition_roc")
    write(metrics, "attrition_metrics")

    banner(f"Attrition (train {len(train):,} / test {len(test):,} snapshots)")
    print(f"held-out AUC {auc:.3f}   base rate {base_rate:.1%}")
    results = {"auc": auc}
    for var, planted in PLANTED.items():
        row = coefs.set_index("variable").loc[var]
        ok = abs(row["odds_ratio"] - planted) <= OR_TOLERANCE and row["or_ci_low"] <= planted <= row["or_ci_high"]
        results[var] = {"odds_ratio": row["odds_ratio"], "ci": (row["or_ci_low"], row["or_ci_high"]), "recovered": ok}
        print(f"{var:<20} OR {row['odds_ratio']:.2f}  95% CI [{row['or_ci_low']:.2f}, {row['or_ci_high']:.2f}]"
              f"  planted {planted}  ->  {'RECOVERED' if ok else 'NOT RECOVERED'}")
    return results


if __name__ == "__main__":
    main()
