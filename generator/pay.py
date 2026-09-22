"""Annual pay review snapshots (1 April) and grade pay bands.

log(base) = log(band mid for grade, year) + offset + tenure + rating + job family + location
            + persistent person effect + yearly noise + log(1 + planted_female_gap) * female
The planted gap is applied AFTER every legitimate factor, so an OLS with those controls
recovers it as the adjusted gap.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from generator import rng_for, to_date


def build_pay_bands(cfg: dict, years: list[int]) -> pd.DataFrame:
    pc = cfg["pay"]
    rows = []
    for y in years:
        idx = (1 + pc["structure_increase_per_year"]) ** (y - 2018)
        for g, mid in pc["grade_midpoint_2018"].items():
            m = mid * idx
            rows.append((g, y, round(m * (1 - pc["band_spread"]), 0), round(m, 0), round(m * (1 + pc["band_spread"]), 0)))
    return pd.DataFrame(rows, columns=["grade_code", "band_year", "band_min", "band_mid", "band_max"])


def assignments_asof(hist: pd.DataFrame, emp_ids: np.ndarray, on: pd.Timestamp) -> pd.DataFrame:
    """Team and job of each employee as of a date (latest non-termination history row)."""
    h = hist[(hist["action_code"] != "TERMINATION") & (hist["effective_date"] <= on)]
    last = h.sort_values(["emp_id", "effective_date"]).groupby("emp_id").tail(1).set_index("emp_id")
    return last.loc[emp_ids, ["team_code", "job_code"]]


def build_salary_history(cfg: dict, sim) -> tuple[pd.DataFrame, pd.DataFrame]:
    pc = cfg["pay"]
    rng = rng_for(cfg, "pay")
    roster = sim.pop["roster"].set_index("emp_id")
    jobs = sim.pop["jobs"].set_index("job_code")
    station = dict(zip(sim.pop["teams"]["team_code"], sim.pop["teams"]["station_code"]))
    hist = sim.job_history()
    years = sim.years
    bands = build_pay_bands(cfg, years)
    mid = {(g, y): m for g, y, m in bands[["grade_code", "band_year", "band_mid"]].itertuples(index=False)}
    year_eps = rng.normal(0, pc["year_sd"], size=(len(years), sim.n))
    gap = np.log(1 + pc["planted_female_gap"])

    frames = []
    for k, y in enumerate(years):
        review = np.datetime64(f"{y}-{pc['review_date_mmdd']}")
        idx = np.flatnonzero((sim.hire <= review) & (np.isnat(sim.exit) | (sim.exit > review)))
        emp = sim.emp_id[idx]
        a = assignments_asof(hist, emp, pd.Timestamp(review))
        grade = jobs.loc[a["job_code"], "grade"].to_numpy()
        family = jobs.loc[a["job_code"], "job_family"].to_numpy()
        loc = np.array([station[t] for t in a["team_code"]])
        tenure = (review - sim.hire[idx]).astype(int) / 365.25
        rating = sim.rating[y - 1][idx]
        female = roster.loc[emp, "gender"].to_numpy() == "F"
        log_base = (np.log([mid[(g, y)] for g in grade]) + pc["offset"]
                    + pc["tenure_effect_per_year"] * np.minimum(tenure, pc["tenure_cap_years"])
                    + pc["rating_effect"] * np.where(rating > 0, rating - 3, 0)
                    + np.array([pc["family_premium"][f] for f in family])
                    + np.array([pc["location_premium"][s] for s in loc])
                    + roster.loc[emp, "pay_u"].to_numpy() + year_eps[k, idx]
                    + gap * female)
        base = np.round(np.exp(log_base), -1)
        high = np.array([int(g[1:]) >= 7 for g in grade])
        housing = np.round(base * np.where(high, pc["housing_allowance_pct"]["high"], pc["housing_allowance_pct"]["low"]), 0)
        flying = np.round(base * np.array([pc["flying_allowance_pct"].get(f, 0.0) for f in family]), 0)
        frames.append(pd.DataFrame({
            "emp_id": emp, "review_date": pd.Timestamp(review), "grade_code": grade, "currency": pc["currency"],
            "base_annual": base, "housing_allowance": housing, "transport_allowance": float(pc["transport_allowance"]),
            "flying_allowance": flying, "change_reason": "Annual review"}))
    sal = pd.concat(frames, ignore_index=True)
    sal.insert(0, "pay_record_id", [f"PAY{i:07d}" for i in range(1, len(sal) + 1)])
    return sal, bands
