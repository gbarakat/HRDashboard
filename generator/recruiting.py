"""Requisitions (one per hire, internal fill, cancellation or open role) and applications.

Every external hire from the event simulation is the accepted candidate of exactly one
requisition, so recruiting, headcount and attrition describe the same people.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from generator import rng_for, to_date

CHANNELS = pd.DataFrame(
    [("INT", "Internal", "Internal"), ("REF", "Referral", "External"), ("LNK", "LinkedIn", "External"),
     ("JBD", "Job board", "External"), ("AGY", "Agency", "External"), ("CMP", "Campus", "External")],
    columns=["source_code", "source_name", "source_type"])
CODE = dict(zip(CHANNELS["source_name"], CHANNELS["source_code"]))
PROGRESS_WEIGHT = {"Internal": 3.0, "Referral": 2.5, "Agency": 2.0, "Campus": 1.0, "LinkedIn": 1.0, "Job board": 0.8}
STAGES = {1: "APPLIED", 2: "SCREENED", 3: "INTERVIEWED", 4: "OFFERED", 5: "HIRED"}


def _days(rng, lo_hi, n, scale=1.0):
    lo, hi = lo_hi
    return np.round(rng.integers(lo, hi + 1, n) * scale).astype("timedelta64[D]")


def build_requisitions(cfg: dict, sim) -> tuple[pd.DataFrame, pd.DataFrame]:
    rc = cfg["recruiting"]
    rng = rng_for(cfg, "recruiting")
    jobs = sim.pop["jobs"].set_index("job_code")
    end = np.datetime64(to_date(cfg["dates"]["end"]))
    start = np.datetime64(to_date(cfg["dates"]["start"]))
    hist = sim.job_history()

    # ---- filled externally: every hire in the window
    hires = hist[(hist["action_code"] == "HIRE") & (hist["effective_date"] >= pd.Timestamp(start))].copy()
    hires = hires.rename(columns={"emp_id": "hired_emp_id", "effective_date": "start_on"})
    hires["fill_type"] = "External"
    grade = jobs.loc[hires["job_code"], "grade_no"].to_numpy()
    critical = jobs.loc[hires["job_code"], "is_critical"].to_numpy()
    month = hires["start_on"].dt.month.to_numpy()
    share = rc["channel_hire_share"]
    names = list(share)
    w = np.tile(np.array([share[c] for c in names]), (len(hires), 1))
    w[:, names.index("Campus")] *= np.where(grade <= 5, 1.0, 0.0) * np.where(np.isin(month, [9, 10]), 2.0, 1.0)
    w[:, names.index("Agency")] *= np.where((grade >= 8) | critical, 2.5, 1.0)
    w /= w.sum(axis=1, keepdims=True)
    hires["source"] = [names[rng.choice(len(names), p=p)] for p in w]

    # ---- filled internally: moves via a posted requisition
    fills = pd.DataFrame(sim.internal_fills, columns=["i", "start_on", "team_code", "job_code",
                                                      "from_team", "from_job", "requisition_ref"])
    fills["hired_emp_id"] = sim.emp_id[fills["i"]]
    fills["start_on"] = pd.to_datetime(fills["start_on"])
    fills["fill_type"] = "Internal"
    fills["source"] = "Internal"

    filled = pd.concat([hires[["hired_emp_id", "start_on", "team_code", "job_code", "fill_type", "source"]],
                        fills[["hired_emp_id", "start_on", "team_code", "job_code", "fill_type", "source",
                               "requisition_ref"]]], ignore_index=True)
    n = len(filled)
    crit = jobs.loc[filled["job_code"], "is_critical"].to_numpy()
    st = filled["start_on"].to_numpy().astype("datetime64[D]")
    internal = (filled["fill_type"] == "Internal").to_numpy()
    accept = st - np.where(internal, _days(rng, (7, 30), n), _days(rng, rc["days_accept_to_start"], n))
    offer = accept - _days(rng, rc["days_offer_to_accept"], n)
    screen = offer - np.where(crit, _days(rng, rc["days_screen_to_offer"], n, 1.6),
                              _days(rng, rc["days_screen_to_offer"], n))
    opened = screen - _days(rng, rc["days_open_to_screen"], n)
    filled["opened_on"], filled["first_screen_on"] = opened, screen
    filled["offer_on"], filled["offer_accepted_on"] = offer, accept
    filled["req_status"] = "Filled"
    filled["closed_on"] = accept

    # ---- cancelled and still-open requisitions (same team/job mix as real demand)
    n_cancel = int(round(rc["cancelled_share"] * n / (1 - rc["cancelled_share"])))
    pick = filled.sample(n_cancel + rc["open_at_end"], random_state=cfg["seed"])[["team_code", "job_code"]]
    extra = pick.reset_index(drop=True)
    k = len(extra)
    status = np.array(["Cancelled"] * n_cancel + ["Open"] * rc["open_at_end"])
    span = (np.datetime64("2025-09-01") - start).astype(int)
    opened_x = np.where(status == "Cancelled",
                        start + rng.integers(0, span, k).astype("timedelta64[D]"),
                        np.datetime64("2025-09-01") + rng.integers(0, 110, k).astype("timedelta64[D]"))
    screen_x = opened_x + _days(rng, rc["days_open_to_screen"], k)
    extra["opened_on"] = opened_x
    extra["first_screen_on"] = np.where(screen_x <= end, screen_x, np.datetime64("NaT"))
    extra["offer_on"] = np.datetime64("NaT")
    extra["offer_accepted_on"] = np.datetime64("NaT")
    extra["start_on"] = pd.NaT
    extra["req_status"] = status
    extra["closed_on"] = np.where(status == "Cancelled", screen_x + _days(rng, (10, 60), k), np.datetime64("NaT"))
    extra["fill_type"] = None
    extra["source"] = None
    extra["hired_emp_id"] = None

    reqs = pd.concat([filled, extra], ignore_index=True)
    reqs["opened_on"] = pd.to_datetime(reqs["opened_on"])
    reqs = reqs.sort_values(["opened_on", "team_code", "job_code"], kind="stable").reset_index(drop=True)
    reqs.insert(0, "req_id", [f"R{i:06d}" for i in range(1, len(reqs) + 1)])

    # ---- costs
    yr = reqs["opened_on"].dt.year.clip(lower=start.astype("datetime64[Y]").astype(int) + 1970)
    mid = np.array([cfg["pay"]["grade_midpoint_2018"][f"G{g}"] for g in jobs.loc[reqs["job_code"], "grade_no"]])
    base_est = mid * (1 + cfg["pay"]["structure_increase_per_year"]) ** (yr - 2018)
    ext = rc["external_cost"]
    cost = [0.0 if s is None else (ext["Agency"] * b if s == "Agency" else float(ext[s]))
            for s, b in zip(reqs["source"], base_est)]
    reqs["external_cost_usd"] = np.round(cost, 2)
    hours = rng.integers(rc["recruiter_hours"][0], rc["recruiter_hours"][1] + 1, len(reqs))
    reqs["recruiter_hours"] = np.where(reqs["req_status"] == "Filled", hours, (hours * 0.5).round())
    reqs["hire_source_code"] = reqs["source"].map(CODE)

    apps = build_applications(cfg, rng, sim, reqs)
    for c in ["first_screen_on", "offer_on", "offer_accepted_on", "start_on", "closed_on"]:
        reqs[c] = pd.to_datetime(reqs[c])
    reqs = reqs[["req_id", "team_code", "job_code", "opened_on", "first_screen_on", "offer_on", "offer_accepted_on",
                 "start_on", "closed_on", "req_status", "fill_type", "hire_source_code", "hired_emp_id",
                 "requisition_ref", "external_cost_usd", "recruiter_hours"]]
    return reqs, apps


def build_applications(cfg: dict, rng, sim, reqs: pd.DataFrame) -> pd.DataFrame:
    rc = cfg["recruiting"]
    jobs = sim.pop["jobs"].set_index("job_code")
    grade = jobs.loc[reqs["job_code"], "grade_no"].to_numpy()
    filled = (reqs["req_status"] == "Filled").to_numpy()
    hires_by = reqs.loc[filled, "source"].value_counts()
    names = list(rc["channel_yield"])
    # non-hired applicants per requisition so that realised yields match the targets
    eligible = {c: (grade <= 5) if c == "Campus" else np.ones(len(reqs), bool) for c in names}
    lam = {c: (hires_by.get(c, 0) / rc["channel_yield"][c] - hires_by.get(c, 0)) / eligible[c].sum() for c in names}

    opened = reqs["opened_on"].to_numpy().astype("datetime64[D]")
    screen = reqs["first_screen_on"].to_numpy().astype("datetime64[D]")
    offer = reqs["offer_on"].to_numpy().astype("datetime64[D]")
    end = np.datetime64(to_date(cfg["dates"]["end"]))
    decline_rate = rc["offer_decline_rate"]
    rows = []
    for r in range(len(reqs)):
        last_apply = screen[r] + np.timedelta64(10, "D") if not np.isnat(screen[r]) else opened[r] + np.timedelta64(30, "D")
        last_apply = min(last_apply, offer[r] if not np.isnat(offer[r]) else last_apply, end)
        window = max(1, (last_apply - opened[r]).astype(int))
        pool = []
        for c in names:
            if eligible[c][r]:
                pool += [c] * rng.poisson(lam[c])
        pool = np.array(pool, dtype=object)
        stage = np.ones(len(pool), dtype=int)
        if len(pool):
            wts = np.array([PROGRESS_WEIGHT[c] for c in pool])
            order = rng.choice(len(pool), size=len(pool), replace=False, p=wts / wts.sum())
            n_off = rng.poisson(decline_rate / (1 - decline_rate)) if filled[r] else 0
            n_int = rng.poisson(3.0) if not np.isnat(screen[r]) else 0
            n_scr = rng.poisson(5.0) if not np.isnat(screen[r]) else 0
            stage[order[:n_off]] = 4
            stage[order[n_off:n_off + n_int]] = np.maximum(stage[order[n_off:n_off + n_int]], 3)
            stage[order[n_off + n_int:n_off + n_int + n_scr]] = np.maximum(stage[order[n_off + n_int:n_off + n_int + n_scr]], 2)
        applied = opened[r] + rng.integers(0, window, len(pool)).astype("timedelta64[D]")
        for c, s, d in zip(pool, stage, applied):
            rows.append((reqs.at[r, "req_id"], c, int(s), d, None))
        if filled[r]:
            d = opened[r] + np.timedelta64(int(rng.integers(0, max(1, (screen[r] - opened[r]).astype(int)))), "D")
            rows.append((reqs.at[r, "req_id"], reqs.at[r, "source"], 5, d, reqs.at[r, "hired_emp_id"]))

    apps = pd.DataFrame(rows, columns=["req_id", "source", "stage_no", "applied_on", "hired_emp_id"])
    apps["applied_on"] = pd.to_datetime(apps["applied_on"])
    apps = apps.sort_values(["applied_on", "req_id"], kind="stable").reset_index(drop=True)
    apps.insert(0, "application_id", [f"A{i:07d}" for i in range(1, len(apps) + 1)])

    # internal applicants are existing employees; external ones get a candidate id
    internal = apps["source"] == "Internal"
    apps["internal_emp_id"] = np.where(internal & apps["hired_emp_id"].notna(), apps["hired_emp_id"], None)
    for a in np.flatnonzero((internal & apps["hired_emp_id"].isna()).to_numpy()):
        d = np.datetime64(apps.at[a, "applied_on"], "D")
        active = np.flatnonzero((sim.hire <= d) & (np.isnat(sim.exit) | (sim.exit > d)))
        apps.at[a, "internal_emp_id"] = sim.emp_id[rng.choice(active)]
    apps["candidate_id"] = np.where(internal, "EMP-" + apps["internal_emp_id"].fillna(""),
                                    [f"C{i:07d}" for i in range(1, len(apps) + 1)])
    apps["source_code"] = apps["source"].map(CODE)
    apps["furthest_stage"] = apps["stage_no"].map(STAGES)
    apps["hired_emp_id"] = np.where(apps["stage_no"] == 5, apps["hired_emp_id"], None)
    return apps[["application_id", "req_id", "candidate_id", "source_code", "applied_on", "furthest_stage",
                 "internal_emp_id", "hired_emp_id"]]
