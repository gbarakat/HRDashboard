"""Reference data (org, jobs, stations) and the base roster of 6,000 employees."""
from __future__ import annotations

import numpy as np
import pandas as pd

from generator import days, load_config, rng_for, to_date

# --------------------------------------------------------------------------- org
# division -> department -> (share of headcount, job family, {section: [stations of its teams]})
HUB, MRO = "HUB", "MRO"
OUTSTATIONS = ["LHR", "FRA", "BOM", "SIN"]
ORG = {
    "Flight Operations": {
        "Flight Deck": (0.12, "Flight Deck", {"A320 Fleet": [HUB] * 3, "B787 Fleet": [HUB] * 2, "A350 Fleet": [HUB] * 2}),
        "Cabin Services": (0.25, "Cabin Crew", {"Narrowbody Cabin": [HUB] * 3, "Widebody Cabin": [HUB] * 3, "Premium Cabin": [HUB] * 2}),
        "Crew Planning": (0.03, "Operations Control", {"Crew Rostering": [HUB] * 2, "Crew Tracking": [HUB] * 2}),
        "Flight Dispatch": (0.02, "Operations Control", {"Dispatch": [HUB] * 2, "Flight Planning": [HUB]}),
        "Safety & Training": (0.025, "Operations Control", {"Flight Safety": [HUB], "Training Delivery": [HUB] * 2}),
    },
    "Technical Operations": {
        "Line Maintenance": (0.08, "Engineering", {"Hub Line": [HUB] * 3, "Outstation Line": OUTSTATIONS}),
        "Base Maintenance": (0.07, "Engineering", {"Heavy Checks": [MRO] * 3, "Cabin Interiors": [MRO]}),
        "Component Shop": (0.03, "Engineering", {"Avionics": [MRO], "Wheels & Brakes": [MRO], "Engines": [MRO]}),
        "Technical Records": (0.012, "Corporate Functions", {"Records": [MRO], "Airworthiness": [MRO]}),
        "Engineering Planning": (0.015, "Corporate Functions", {"Maintenance Planning": [MRO], "Reliability": [MRO]}),
    },
    "Commercial": {
        "Sales": (0.03, "Commercial", {"Corporate Sales": [HUB], "Distribution": [HUB], "Regional Sales": OUTSTATIONS}),
        "Revenue Management": (0.015, "Commercial", {"Pricing": [HUB], "Network Analytics": [HUB]}),
        "Airport Services": (0.14, "Airport Services", {"Passenger Services": [HUB] * 3, "Ramp Operations": [HUB] * 3,
                                                          "Baggage Services": [HUB] * 2, "Outstation Handling": OUTSTATIONS}),
        "Customer Care": (0.04, "Airport Services", {"Contact Centre": [HUB] * 2, "Customer Relations": [HUB]}),
        "Loyalty & Marketing": (0.015, "Commercial", {"Loyalty": [HUB], "Brand & Digital": [HUB]}),
    },
    "Corporate Services": {
        "Finance": (0.025, "Corporate Functions", {"Accounting": [HUB], "FP&A": [HUB], "Treasury": [HUB]}),
        "Human Resources": (0.02, "Corporate Functions", {"HR Operations": [HUB], "Talent": [HUB], "Reward": [HUB]}),
        "Information Technology": (0.03, "Corporate Functions", {"Infrastructure": [HUB], "Applications": [HUB] * 2}),
        "Procurement": (0.012, "Corporate Functions", {"Strategic Sourcing": [HUB], "Fuel & Contracts": [HUB]}),
        "Legal & Compliance": (0.01, "Corporate Functions", {"Legal": [HUB], "Compliance": [HUB]}),
    },
}
OUTSTATION_TEAM_WEIGHT = 0.35   # outstation teams are smaller than hub teams

STATIONS = pd.DataFrame(
    [("HUB", "Central Hub", "Hub City", "Home", "Hub", True),
     ("MRO", "Maintenance Base", "Hub City", "Home", "Hub", False),
     ("LHR", "London Heathrow", "London", "United Kingdom", "Europe", False),
     ("FRA", "Frankfurt", "Frankfurt", "Germany", "Europe", False),
     ("BOM", "Mumbai", "Mumbai", "India", "Asia", False),
     ("SIN", "Singapore Changi", "Singapore", "Singapore", "Asia", False)],
    columns=["station_code", "station_name", "city", "country", "region", "is_hub"])

# ---------------------------------------------------------------------- job ladders
# family -> [(title, grade, pyramid weight, critical)] from lowest to highest rung
LADDERS = {
    "Flight Deck": [("Second Officer", 7, 0.15, False), ("First Officer", 8, 0.40, False),
                    ("Captain", 10, 0.38, True), ("Training Captain", 11, 0.07, True)],
    "Cabin Crew": [("Cabin Crew", 3, 0.55, False), ("Senior Cabin Crew", 4, 0.25, False),
                   ("Cabin Supervisor", 5, 0.12, False), ("Purser", 6, 0.08, False)],
    "Operations Control": [("Operations Coordinator", 4, 0.35, False), ("Operations Controller", 6, 0.35, False),
                           ("Senior Operations Controller", 7, 0.20, True), ("Operations Control Manager", 9, 0.10, True)],
    "Engineering": [("Aircraft Mechanic", 3, 0.25, False), ("Aircraft Technician", 4, 0.30, False),
                    ("Licensed Engineer", 6, 0.25, True), ("Senior Licensed Engineer", 7, 0.12, True),
                    ("Maintenance Manager", 9, 0.08, False)],
    "Airport Services": [("Ramp Agent", 1, 0.25, False), ("Customer Service Agent", 2, 0.35, False),
                         ("Senior Customer Service Agent", 3, 0.20, False), ("Shift Supervisor", 5, 0.12, False),
                         ("Duty Manager", 7, 0.08, False)],
    "Commercial": [("Sales Executive", 4, 0.30, False), ("Commercial Analyst", 5, 0.30, False),
                   ("Senior Commercial Analyst", 6, 0.20, False), ("Commercial Manager", 8, 0.15, False),
                   ("Head of Commercial", 10, 0.05, True)],
    "Corporate Functions": [("Assistant", 2, 0.15, False), ("Officer", 4, 0.25, False), ("Specialist", 6, 0.25, False),
                            ("Senior Specialist", 7, 0.15, False), ("Manager", 8, 0.12, False),
                            ("Senior Manager", 9, 0.05, False), ("Director", 11, 0.025, True),
                            ("Vice President", 12, 0.005, True)],
}


def build_jobs() -> pd.DataFrame:
    rows, n = [], 0
    for family, ladder in LADDERS.items():
        for rung, (title, grade, _w, critical) in enumerate(ladder):
            n += 1
            rows.append((f"J{n:03d}", title, family, f"G{grade}", grade, rung, critical))
    return pd.DataFrame(rows, columns=["job_code", "job_title", "job_family", "grade", "grade_no", "rung", "is_critical"])


def build_teams() -> pd.DataFrame:
    """One row per team (natural key team_code) with its original position in the hierarchy."""
    rows, n = [], 0
    for division, depts in ORG.items():
        for dept, (share, family, sections) in depts.items():
            for section, stations in sections.items():
                for i, station in enumerate(stations, start=1):
                    n += 1
                    name = f"{section} {station}" if len(set(stations)) > 1 else f"{section} {i}"
                    weight = OUTSTATION_TEAM_WEIGHT if station in OUTSTATIONS else 1.0
                    rows.append((f"T{n:03d}", name, section, dept, division, station, family, share, weight))
    return pd.DataFrame(rows, columns=["team_code", "team_name", "section", "department", "division",
                                       "station_code", "job_family", "dept_share", "team_weight"])


def build_org_units(cfg: dict, teams: pd.DataFrame) -> pd.DataFrame:
    """Effective-dated org hierarchy. The re-org moves one department to another division."""
    reorg = cfg["mobility"]["reorg"]
    reorg_date = to_date(reorg["date"])
    base = teams[["team_code", "team_name", "section", "department", "division", "station_code"]].copy()
    base["effective_from"] = pd.Timestamp("1990-01-01").date()
    base["effective_to"] = pd.NaT
    moved = base["department"] == reorg["department"]
    before = base[moved].copy()
    before["effective_to"] = (pd.Timestamp(reorg_date) - pd.Timedelta(days=1)).date()
    after = base[moved].copy()
    after["division"] = reorg["to_division"]
    after["effective_from"] = reorg_date
    out = pd.concat([base[~moved], before, after], ignore_index=True)
    return out.sort_values(["team_code", "effective_from"]).reset_index(drop=True)


# ------------------------------------------------------------------------ roster
def _dept_table(teams: pd.DataFrame) -> pd.DataFrame:
    d = teams.groupby(["department", "division", "job_family"], as_index=False)["dept_share"].first()
    d["p"] = d["dept_share"] / d["dept_share"].sum()
    return d


def _pick_teams(rng, teams: pd.DataFrame, depts: np.ndarray) -> np.ndarray:
    out = np.empty(len(depts), dtype=object)
    for dept in np.unique(depts):
        idx = np.flatnonzero(depts == dept)
        t = teams[teams["department"] == dept]
        w = t["team_weight"].to_numpy()
        out[idx] = rng.choice(t["team_code"].to_numpy(), size=len(idx), p=w / w.sum())
    return out


def _female_prob(cfg, family: np.ndarray, rung: np.ndarray) -> np.ndarray:
    base = np.array([cfg["population"]["female_share_by_family"][f] for f in family])
    top = np.array([len(LADDERS[f]) - 1 for f in family])
    decline = cfg["population"]["female_decline_to_top"]
    return base * (1 - decline * np.divide(rung, top, out=np.zeros(len(rung)), where=top > 0))


def build_roster(cfg: dict) -> dict[str, pd.DataFrame]:
    rng = rng_for(cfg, "population")
    pc = cfg["population"]
    start = to_date(cfg["dates"]["start"])
    opening_date = np.datetime64(start) - np.timedelta64(1, "D")          # 2017-12-31
    n_total, n_open = pc["total_employees"], pc["opening_headcount"]
    n_new = n_total - n_open
    years = list(range(start.year, to_date(cfg["dates"]["end"]).year + 1))
    assert n_new == cfg["hiring"]["hires_per_year"] * len(years), "hires_per_year x years must equal total - opening"

    teams = build_teams()
    dept = _dept_table(teams)

    # --- opening population: tenure first, rung follows tenure within family
    # truncated exponential tenure (no pile-up at the cap)
    mean_t, cap_t = pc["opening_tenure_mean_years"], 27.5
    tenure_y = 0.08 - mean_t * np.log(1 - rng.random(n_open) * (1 - np.exp(-cap_t / mean_t)))
    dep_open = rng.choice(dept["department"].to_numpy(), size=n_open, p=dept["p"].to_numpy())
    # --- new hires: 400 a year, planted Sep-Nov seasonality
    mw = cfg["hiring"]["month_weights"]
    months = np.array(sorted(mw))
    probs = np.array([mw[m] for m in months], dtype=float)
    hire_new = []
    for y in years:
        counts = rng.multinomial(cfg["hiring"]["hires_per_year"], probs / probs.sum())
        for m, c in zip(months, counts):
            first = np.datetime64(f"{y}-{m:02d}-01")
            last = (first.astype("datetime64[M]") + 1).astype("datetime64[D]")
            hire_new.append(first + rng.integers(0, (last - first).astype(int), size=c))
    hire_new = np.sort(np.concatenate(hire_new))
    dep_new = rng.choice(dept["department"].to_numpy(), size=n_new, p=dept["p"].to_numpy())

    departments = np.concatenate([dep_open, dep_new])
    fam_of = dict(zip(dept["department"], dept["job_family"]))
    family = np.array([fam_of[d] for d in departments])
    is_open = np.r_[np.ones(n_open, bool), np.zeros(n_new, bool)]

    rung = np.zeros(n_total, dtype=int)
    for fam, ladder in LADDERS.items():
        w = np.array([r[2] for r in ladder])
        # opening: sample rungs from the pyramid, hand them out in order of (noisy) tenure
        idx = np.flatnonzero(is_open & (family == fam))
        if len(idx):
            rungs = np.sort(rng.choice(len(ladder), size=len(idx), p=w / w.sum()))
            order = np.argsort(tenure_y[idx] + rng.normal(0, 4, len(idx)))
            rung[idx[order]] = rungs
        # new hires: entry-heavy
        idx = np.flatnonzero(~is_open & (family == fam))
        if len(idx):
            wn = w * 0.30 ** np.arange(len(ladder))
            rung[idx] = rng.choice(len(ladder), size=len(idx), p=wn / wn.sum())

    top = np.array([len(LADDERS[f]) - 1 for f in family])
    rung_frac = np.divide(rung, top, out=np.zeros(n_total), where=top > 0)
    age_at_hire = np.clip(rng.normal(24 + 14 * rung_frac, 3.5), 19, 55)
    # the opening population cannot be older than 63 on day one: shorten tenure instead
    too_old = age_at_hire[:n_open] + tenure_y > 63
    tenure_y[too_old] = np.maximum(0.5, 63 - rng.uniform(0, 6, too_old.sum()) - age_at_hire[:n_open][too_old])
    hire_open = opening_date - np.round(tenure_y * 365.25).astype("timedelta64[D]")
    hire_open = np.maximum(hire_open, days(cfg["dates"]["earliest_hire"]))
    hire_date = np.concatenate([hire_open, hire_new])
    birth_date = hire_date - np.round(age_at_hire * 365.25).astype("timedelta64[D]")

    gender = np.where(rng.random(n_total) < _female_prob(cfg, family, rung), "F", "M")
    nat = pc["nationality"]
    nationality = rng.choice(list(nat), size=n_total, p=np.array(list(nat.values())) / sum(nat.values()))
    cm = pc["commute_km"]
    commute = np.clip(np.exp(rng.normal(np.log(cm["median"]), cm["sigma"], n_total)), cm["min"], cm["max"]).round(1)
    fte_levels = np.array(list(pc["fte_mix"]), dtype=float)
    fte_p = np.array(list(pc["fte_mix"].values()))
    fte = rng.choice(fte_levels, size=n_total, p=fte_p / fte_p.sum())
    fte[family == "Flight Deck"] = 1.0
    arch = pc["learner_archetypes"]
    archetype = rng.choice(list(arch), size=n_total, p=np.array(list(arch.values())) / sum(arch.values()))

    team_code = _pick_teams(rng, teams, departments)
    jobs = build_jobs()
    job_lookup = {(f, r): c for f, r, c in jobs[["job_family", "rung", "job_code"]].itertuples(index=False)}

    roster = pd.DataFrame({
        "hire_date": hire_date,
        "birth_date": birth_date,
        "gender": gender,
        "nationality": nationality,
        "commute_km": commute,
        "fte": fte,
        "department": departments,
        "job_family": family,
        "rung": rung,
        "team_code": team_code,
        "learner_archetype": archetype,
        "perf_z": rng.normal(0, 1, n_total),       # persistent performance trait (latent, not exported)
        "learn_z": rng.normal(0, 1, n_total),      # learning propensity (latent, not exported)
        "pay_u": rng.normal(0, cfg["pay"]["person_sd"], n_total),   # persistent pay position (latent)
        "is_opening": is_open,
    })
    roster["job_code"] = [job_lookup[(f, r)] for f, r in zip(roster["job_family"], roster["rung"])]
    # emp_ids follow hire order, like a real HRIS
    roster = roster.sort_values(["hire_date", "team_code"], kind="stable").reset_index(drop=True)
    roster.insert(0, "emp_id", [f"E{i:05d}" for i in range(1, n_total + 1)])
    return {"roster": roster, "teams": teams, "org_units": build_org_units(cfg, teams),
            "jobs": jobs, "stations": STATIONS.copy()}


if __name__ == "__main__":
    out = build_roster(load_config())
    r = out["roster"]
    print(r.head(10).to_string())
    print(len(r), "employees;", r["is_opening"].sum(), "opening;", len(out["teams"]), "teams")
