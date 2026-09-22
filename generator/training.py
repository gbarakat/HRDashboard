"""Course catalogue and annual training completions.

Annual hours = mandatory (by job family) + onboarding (hire year) + discretionary (skewed,
driven by a planted learner archetype). The materialised hours feed the planted
protective effect on attrition in the following year.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# code, title, category, hours, cost per participant (USD), mandatory_for (family, "ALL", "ONBOARDING" or None)
CATALOG = [
    ("C001", "Recurrent Simulator Training", "Safety & Compliance", 12, 4500, "Flight Deck"),
    ("C002", "Emergency Procedures Recurrent", "Safety & Compliance", 4, 300, "Flight Deck"),
    ("C003", "Cabin Safety Recurrent", "Safety & Compliance", 8, 350, "Cabin Crew"),
    ("C004", "First Aid & Aviation Medicine", "Safety & Compliance", 4, 150, "Cabin Crew"),
    ("C005", "Aircraft Type Refresher", "Technical", 8, 900, "Engineering"),
    ("C006", "Human Factors Recurrent", "Safety & Compliance", 4, 120, "Engineering"),
    ("C007", "Operations Control Recurrent", "Safety & Compliance", 6, 400, "Operations Control"),
    ("C008", "Safety Management Systems", "Safety & Compliance", 2, 60, "Operations Control"),
    ("C009", "Dangerous Goods Awareness", "Safety & Compliance", 4, 120, "Airport Services"),
    ("C010", "Aviation Security Awareness", "Safety & Compliance", 2, 40, "Airport Services|Commercial|Corporate Functions"),
    ("C011", "Code of Conduct & Ethics", "Safety & Compliance", 1, 20, "Commercial|Corporate Functions"),
    ("C012", "Corporate Induction", "Onboarding", 8, 250, "ONBOARDING"),
    ("C013", "Airline Operations Fundamentals", "Onboarding", 8, 200, "ONBOARDING"),
    ("C014", "Systems & Tools Onboarding", "Onboarding", 8, 150, "ONBOARDING"),
    ("C015", "Advanced Troubleshooting", "Technical", 16, 1200, None),
    ("C016", "Composite Repair", "Technical", 24, 2000, None),
    ("C017", "Revenue Management Fundamentals", "Technical", 8, 600, None),
    ("C018", "Aircraft Performance", "Technical", 8, 500, None),
    ("C019", "Lean Maintenance", "Technical", 8, 450, None),
    ("C020", "Crew Resource Management Plus", "Technical", 4, 200, None),
    ("C021", "First-Time Manager", "Leadership", 24, 2500, None),
    ("C022", "Coaching for Performance", "Leadership", 8, 700, None),
    ("C023", "Leading Change", "Leadership", 16, 1800, None),
    ("C024", "Strategic Thinking", "Leadership", 8, 900, None),
    ("C025", "Executive Presence", "Leadership", 4, 600, None),
    ("C026", "Data Literacy", "Digital", 4, 150, None),
    ("C027", "Power BI Essentials", "Digital", 8, 300, None),
    ("C028", "Python for Analysts", "Digital", 16, 600, None),
    ("C029", "Cybersecurity Essentials", "Digital", 2, 50, None),
    ("C030", "AI at Work", "Digital", 4, 200, None),
    ("C031", "Service Excellence", "Customer Service", 4, 180, None),
    ("C032", "Handling Difficult Passengers", "Customer Service", 4, 180, None),
    ("C033", "Premium Service Standards", "Customer Service", 8, 400, None),
    ("C034", "Safety Culture Workshop", "Safety & Compliance", 4, 150, None),
    ("C035", "Fatigue Risk Management", "Safety & Compliance", 2, 60, None),
    ("C036", "Anti-Bribery & Corruption", "Safety & Compliance", 1, 20, None),
]

ARCHETYPE_CATEGORIES = {   # elective category preferences per planted learner archetype
    "Compliance only": {"Safety & Compliance": 1.0},
    "Technical deep-diver": {"Technical": 0.75, "Digital": 0.25},
    "Leadership track": {"Leadership": 0.70, "Customer Service": 0.15, "Digital": 0.15},
    "Digital upskiller": {"Digital": 0.75, "Technical": 0.25},
    "Minimal engagement": {},
}


def build_programs() -> pd.DataFrame:
    df = pd.DataFrame(CATALOG, columns=["course_code", "course_title", "category", "hours", "cost_usd", "mandatory_for"])
    df["delivery"] = np.where(df["hours"] >= 8, "Classroom", "e-Learning")
    df.loc[df["course_code"] == "C001", "delivery"] = "Simulator"
    return df


class Trainer:
    def __init__(self, cfg: dict, rng: np.random.Generator, n_emp: int, first_year: int, last_year: int):
        tc = cfg["training"]
        self.cfg, self.rng, self.first_year = tc, rng, first_year
        self.catalog = build_programs()
        self.eps = rng.normal(size=(last_year - first_year + 1, n_emp))
        cat = self.catalog
        self.mandatory = {f: cat[cat["mandatory_for"].fillna("").str.split("|").apply(lambda xs: f in xs)]
                          for f in tc["mandatory_hours_by_family"]}
        self.mandatory_codes = {f: m["course_code"].tolist() for f, m in self.mandatory.items()}
        self.onboarding = cat[cat["mandatory_for"] == "ONBOARDING"]["course_code"].tolist()
        electives = cat[cat["mandatory_for"].isna()]
        self.electives = {c: (g["course_code"].tolist(), g["hours"].tolist()) for c, g in electives.groupby("category")}
        self.course_hours = dict(zip(cat["course_code"], cat["hours"]))

    def _pick_electives(self, target: float, prefs: dict) -> list[str]:
        """Draw elective courses from the archetype's preferred categories until `target` hours are met."""
        chosen: list[str] = []
        remaining = target
        cats = list(prefs)
        w = np.array(list(prefs.values()))
        w = w / w.sum() if len(w) else w
        while remaining > 1.0 and cats:
            codes, hrs = self.electives[cats[self.rng.choice(len(cats), p=w)]]
            pool = [(c, h) for c, h in zip(codes, hrs) if c not in chosen]
            if not pool:
                break
            fits = [ch for ch in pool if ch[1] <= remaining + 4]
            pool = fits or [min(pool, key=lambda ch: ch[1])]
            code, h = pool[self.rng.integers(len(pool))]
            chosen.append(code)
            remaining -= h
        return chosen

    def year(self, year: int, idx: np.ndarray, start: np.ndarray, end: np.ndarray, hire: np.ndarray,
             family: np.ndarray, archetype: np.ndarray, learn_z: np.ndarray) -> tuple[list[tuple], np.ndarray]:
        """Completions for employees `idx` active between start..end (inclusive) in `year`."""
        tc, k = self.cfg, year - self.first_year
        span = (end - start).astype(int) + 1
        frac = span / (366 if year % 4 == 0 else 365)
        mult = np.array([tc["archetype_multiplier"][a] for a in archetype])
        disc = (tc["discretionary_hours_median"] * mult * frac
                * np.exp(tc["discretionary_sigma"] * (0.6 * learn_z + 0.8 * self.eps[k, idx])))
        rows, hours = [], np.zeros(len(idx))
        for j in range(len(idx)):
            codes: list[str] = []
            # mandatory recurrent training once the employee is in role for 3+ months of the year
            if span[j] >= 90:
                codes += self.mandatory_codes[family[j]]
            hired_this_year = hire[j] >= start[j] and hire[j].astype("datetime64[Y]").astype(int) + 1970 == year
            onboarding = self.onboarding if hired_this_year else []
            codes += self._pick_electives(disc[j], ARCHETYPE_CATEGORIES[archetype[j]])
            for code in onboarding:   # within 45 days of hire
                d = hire[j] + np.timedelta64(int(self.rng.integers(0, 45)), "D")
                rows.append((idx[j], code, min(d, end[j])))
            for code in codes:
                rows.append((idx[j], code, start[j] + np.timedelta64(int(self.rng.integers(0, span[j])), "D")))
        pos = {e: n for n, e in enumerate(idx)}
        for e, code, _d in rows:
            hours[pos[e]] += self.course_hours[code]
        return rows, hours
