"""Annual performance ratings (1-5) and potential (1-3), plus the nine-box grid."""
from __future__ import annotations

from functools import lru_cache
from statistics import NormalDist

import numpy as np
import pandas as pd

def _cuts(dist: dict) -> np.ndarray:
    """Standard-normal cut points that split a latent score into the target category shares."""
    shares = np.array([dist[k] for k in sorted(dist)], dtype=float)
    return np.array([NormalDist().inv_cdf(p) for p in np.cumsum(shares / shares.sum())[:-1]])


@lru_cache(maxsize=None)
def _latent_corr(target: float, rating_dist: tuple, pot_dist: tuple) -> float:
    """Latent correlation that yields `target` Pearson r between the discretised scores."""
    rc, pc = _cuts(dict(rating_dist)), _cuts(dict(pot_dist))
    g = np.random.default_rng(42)   # calibration sample, same global seed
    z, e = g.normal(size=400_000), g.normal(size=400_000)
    lo, hi = target, min(0.99, target * 2)
    for _ in range(40):
        rho = (lo + hi) / 2
        r = np.corrcoef(np.digitize(z, rc), np.digitize(rho * z + np.sqrt(1 - rho**2) * e, pc))[0, 1]
        lo, hi = (rho, hi) if r < target else (lo, rho)
    return (lo + hi) / 2


class Reviewer:
    """Draws ratings for any subset of employees; noise is pre-drawn per (year, employee)
    so a person's rating never depends on who else happens to be active."""

    def __init__(self, cfg: dict, rng: np.random.Generator, perf_z: np.ndarray, first_year: int, last_year: int):
        pc = cfg["performance"]
        self.w = pc["persistent_weight"]
        self.rating_cuts = _cuts(pc["rating_distribution"])
        self.pot_cuts = _cuts(pc["potential_distribution"])
        self.rho = _latent_corr(pc["rating_potential_corr"],
                                tuple(sorted(pc["rating_distribution"].items())),
                                tuple(sorted(pc["potential_distribution"].items())))
        self.first_year = first_year
        n_years, n = last_year - first_year + 1, len(perf_z)
        self.perf_z = perf_z
        self.eps_r = rng.normal(size=(n_years, n))
        self.eps_p = rng.normal(size=(n_years, n))

    def draw(self, year: int, idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        k = year - self.first_year
        z = self.w * self.perf_z[idx] + np.sqrt(1 - self.w**2) * self.eps_r[k, idx]
        rating = np.digitize(z, self.rating_cuts) + 1
        pz = self.rho * z + np.sqrt(1 - self.rho**2) * self.eps_p[k, idx]
        potential = np.digitize(pz, self.pot_cuts) + 1
        return rating, potential


def build_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """reviews: emp_id, review_year, rating, potential -> perf_reviews raw table (nine-box is derived in dbt)."""
    out = reviews.sort_values(["review_year", "emp_id"]).reset_index(drop=True)
    out["review_date"] = pd.to_datetime(out["review_year"].astype(str) + "-12-31")
    out.insert(0, "review_id", [f"PR{i:06d}" for i in range(1, len(out) + 1)])
    return out[["review_id", "emp_id", "review_year", "review_date", "rating", "potential"]]
