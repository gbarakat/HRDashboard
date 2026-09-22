"""One population, simulated year by year: exits, hires, promotions, moves, re-org.

Each year Y:
  1. Employees active on 31-Dec of Y-1 (the snapshot) draw a voluntary-exit outcome for Y from
     P = logistic(intercept + planted effects). Other exit types are drawn only if no voluntary exit.
  2. New hires of Y face a monthly hazard by tenure month (low in months 0-2, highest 3-12).
  3. Promotions (1 Apr), lateral moves, internal requisition fills and the re-org are applied in date order.
  4. Training completions are generated for everyone active in Y (hours feed step 1 of Y+1).
  5. Ratings are drawn on 31-Dec of Y for everyone active with 3+ months of service.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from generator import completed_years, load_config, rng_for, to_date
from generator.performance import Reviewer
from generator.population import LADDERS, build_roster
from generator.training import Trainer

NAT = np.datetime64("NaT", "D")
TENURE_BANDS = [(183, "0-6m"), (365, "6-12m"), (730, "1-2y"), (1826, "2-5y"), (3652, "5-10y")]


def tenure_band(tenure_days: np.ndarray) -> np.ndarray:
    out = np.full(len(tenure_days), "10y+", dtype=object)
    for limit, label in reversed(TENURE_BANDS):
        out[tenure_days < limit] = label
    return out


def _step(table: dict, x: np.ndarray) -> np.ndarray:
    """Lookup where `table` maps a lower bound to a value (value of the largest key <= x)."""
    keys = np.array(sorted(table))
    vals = np.array([table[k] for k in keys])
    pos = np.searchsorted(keys, x, side="right") - 1
    return np.where(pos >= 0, vals[np.clip(pos, 0, None)], 0.0)


def _expit(x):
    return 1 / (1 + np.exp(-x))


def _logit(p):
    return np.log(p / (1 - p))


def _year_days(y: int) -> tuple[np.datetime64, np.datetime64]:
    return np.datetime64(f"{y}-01-01"), np.datetime64(f"{y}-12-31")


class Simulation:
    def __init__(self, cfg: dict, pop: dict):
        self.cfg, self.pop = cfg, pop
        r = pop["roster"]
        self.n = len(r)
        self.rng = rng_for(cfg, "events")
        self.start, self.end = to_date(cfg["dates"]["start"]), to_date(cfg["dates"]["end"])
        self.years = list(range(self.start.year, self.end.year + 1))
        self.emp_id = r["emp_id"].to_numpy()
        self.hire = r["hire_date"].to_numpy().astype("datetime64[D]")
        self.birth = r["birth_date"].to_numpy().astype("datetime64[D]")
        self.family = r["job_family"].to_numpy()
        self.rung = r["rung"].to_numpy().copy()
        self.team = r["team_code"].to_numpy().copy()
        self.commute_gt_30 = r["commute_km"].to_numpy() > 30
        self.archetype = r["learner_archetype"].to_numpy()
        self.learn_z = r["learn_z"].to_numpy()
        self.top_rung = np.array([len(LADDERS[f]) - 1 for f in self.family])
        self.exit = np.full(self.n, NAT)
        self.exit_type = np.full(self.n, None, dtype=object)
        self.regretted = np.zeros(self.n, dtype=bool)
        self.notice = np.full(self.n, NAT)

        jobs = pop["jobs"]
        self.job_code = {(f, k): c for f, k, c in jobs[["job_family", "rung", "job_code"]].itertuples(index=False)}
        self.critical = {(f, k): c for f, k, c in jobs[["job_family", "rung", "is_critical"]].itertuples(index=False)}
        self.grade_no = {(f, k): g for f, k, g in jobs[["job_family", "rung", "grade_no"]].itertuples(index=False)}
        teams = pop["teams"]
        self.team_dept = dict(zip(teams["team_code"], teams["department"]))
        self.team_station = dict(zip(teams["team_code"], teams["station_code"]))
        self.team_family = dict(zip(teams["team_code"], teams["job_family"]))
        self.teams = teams

        first, last = self.start.year - 1, self.end.year
        self.reviewer = Reviewer(cfg, rng_for(cfg, "performance"), r["perf_z"].to_numpy(), first, last)
        self.trainer = Trainer(cfg, rng_for(cfg, "training"), self.n, first, last)
        self.rating = {y: np.zeros(self.n, dtype=int) for y in range(first, last + 1)}
        self.potential = {y: np.zeros(self.n, dtype=int) for y in range(first, last + 1)}
        self.hours = {y: np.zeros(self.n) for y in range(first, last + 1)}
        self.history: list[tuple] = []        # emp_idx, date, action, reason, team, job, ref
        self.completions: list[tuple] = []    # emp_idx, course_code, date
        self.internal_fills: list[tuple] = []  # emp_idx, date, to_team, to_job, from_team, from_job, ref

    # ------------------------------------------------------------------ helpers
    def _job(self, i: int) -> str:
        return self.job_code[(self.family[i], self.rung[i])]

    def _active_on(self, d: np.datetime64) -> np.ndarray:
        return (self.hire <= d) & (np.isnat(self.exit) | (self.exit > d))

    def _record(self, i, d, action, reason=None, ref=None):
        self.history.append((i, d, action, reason, self.team[i], self._job(i), ref))

    # ------------------------------------------------------------ opening state
    def _opening_history(self):
        """Pre-2018 careers of the opening population: hired lower, promoted every ~3.5 years."""
        opening = np.datetime64(self.start) - np.timedelta64(1, "D")
        idx = np.flatnonzero(self.hire <= opening)
        for i in idx:
            tenure = (opening - self.hire[i]).astype(int)
            n_promos = int(min(self.rung[i], tenure // int(3.5 * 365)))
            current = self.rung[i]
            self.rung[i] = current - n_promos
            self._record(i, self.hire[i], "HIRE", "New hire")
            for k in range(1, n_promos + 1):
                d = self.hire[i] + np.timedelta64(int(tenure * k / (n_promos + 1)), "D")
                self.rung[i] += 1
                self._record(i, d, "PROMOTION", "Promotion")
        # latent 2017 performance and training (not exported; drive 2018 outcomes)
        y = self.start.year - 1
        y0, y1 = _year_days(y)
        rated = idx[self.hire[idx] <= y1 - np.timedelta64(self.cfg["performance"]["min_tenure_days_for_rating"], "D")]
        self.rating[y][rated], self.potential[y][rated] = self.reviewer.draw(y, rated)
        s = np.maximum(self.hire[idx], y0)
        _rows, h = self.trainer.year(y, idx, s, np.full(len(idx), y1), self.hire[idx], self.family[idx],
                                     self.archetype[idx], self.learn_z[idx])
        self.hours[y][idx] = h

    # --------------------------------------------------------------- one year
    def _snapshot_exits(self, y: int):
        ac = self.cfg["attrition"]
        y0, y1 = _year_days(y)
        snap = y0 - np.timedelta64(1, "D")
        S = np.flatnonzero(self._active_on(snap))
        band = tenure_band((snap - self.hire[S]).astype(int))
        age = completed_years(self.birth[S], np.full(len(S), snap))
        r_prev = self.rating[y - 1][S]
        rating_eff = np.select([r_prev == 0, r_prev <= 2, r_prev == 3], [ac["rating_effects"]["none"],
                               ac["rating_effects"]["low"], ac["rating_effects"]["mid"]], ac["rating_effects"]["high"])
        eta = (ac["intercept"]
               + np.array([ac["tenure_band_effects"][b] for b in band])
               + np.log(ac["planted_odds_ratio_commute_gt_30km"]) * self.commute_gt_30[S]
               + np.log(ac["planted_odds_ratio_training_gt_20h"]) * (self.hours[y - 1][S] > 20)
               + rating_eff
               + ac["age_lt_30_effect"] * (age < 30))
        p_vol = _expit(eta)
        inv_tab = ac["involuntary_by_rating"]
        p_inv = np.array([inv_tab["none"] if r == 0 else inv_tab[int(r)] for r in r_prev])
        p_ret = _step(ac["retirement_by_age"], age)
        p_tr = np.full(len(S), ac["transfer"])
        u, u2 = self.rng.random(len(S)), self.rng.random(len(S))
        day = y0 + self.rng.integers(0, (y1 - y0).astype(int) + 1, len(S)).astype("timedelta64[D]")
        vol = u < p_vol
        inv = ~vol & (u2 < p_inv)
        ret = ~vol & ~inv & (u2 < p_inv + p_ret)
        tr = ~vol & ~inv & ~ret & (u2 < p_inv + p_ret + p_tr)
        for mask, kind in [(vol, "Voluntary"), (inv, "Involuntary"), (ret, "Retirement"), (tr, "Transfer")]:
            self.exit[S[mask]] = day[mask]
            self.exit_type[S[mask]] = kind
        pot_prev = self.potential[y - 1][S]
        crit = np.array([self.critical[(self.family[i], self.rung[i])] for i in S])
        self.regretted[S[vol]] = ((r_prev >= 4) | (pot_prev == 3) | crit)[vol]

    def _new_hire_exits(self, y: int):
        ac = self.cfg["attrition"]
        y0, y1 = _year_days(y)
        H = np.flatnonzero((self.hire >= y0) & (self.hire <= y1))
        for i in H:
            self._record(i, self.hire[i], "HIRE", "New hire")
        age = completed_years(self.birth[H], self.hire[H])
        shift = (np.log(ac["planted_odds_ratio_commute_gt_30km"]) * self.commute_gt_30[H]
                 + ac["age_lt_30_effect"] * (age < 30))
        alive = np.ones(len(H), dtype=bool)
        for m in range(12):
            m0 = self.hire[H] + np.timedelta64(int(round(m * 30.44)), "D")
            at_risk = alive & (m0 <= y1)
            hv = _expit(_logit(_step(ac["new_hire_monthly_voluntary"], np.full(len(H), m))) + shift)
            hi = _step(ac["new_hire_monthly_involuntary"], np.full(len(H), m))
            u = self.rng.random(len(H))
            day = m0 + self.rng.integers(0, 30, len(H)).astype("timedelta64[D]")
            day = np.minimum(day, y1)
            vol = at_risk & (u < hv)
            inv = at_risk & ~vol & (u < hv + hi)
            for mask, kind in [(vol, "Voluntary"), (inv, "Involuntary")]:
                self.exit[H[mask]] = day[mask]
                self.exit_type[H[mask]] = kind
            self.regretted[H[vol]] = [self.critical[(self.family[i], self.rung[i])] for i in H[vol]]
            alive &= ~(vol | inv)

    def _target_team(self, i: int, prefer_other_dept: bool) -> str | None:
        t = self.teams
        cur = self.team[i]
        pool = t[(t["job_family"] == self.family[i]) & (t["station_code"] == self.team_station[cur])
                 & (t["team_code"] != cur)]
        if pool.empty:
            return None
        same = pool[pool["department"] == self.team_dept[cur]]
        other = pool[pool["department"] != self.team_dept[cur]]
        want_other = prefer_other_dept if self.rng.random() < 0.7 else not prefer_other_dept
        pick = other if (want_other and not other.empty) or same.empty else same
        return pick["team_code"].iloc[self.rng.integers(len(pick))]

    def _moves(self, y: int):
        mc = self.cfg["mobility"]
        y0, y1 = _year_days(y)
        promo_date = np.datetime64(f"{y}-{mc['promotion_date_mmdd']}")
        reorg_date = np.datetime64(to_date(mc["reorg"]["date"]))
        reserved = {promo_date, reorg_date}
        plan: list[tuple] = []   # (date, order, kind, emp)

        # promotions on 1 April, driven by last year's rating
        r_prev = self.rating[y - 1]
        eligible = (self._active_on(promo_date) & (self.hire <= promo_date - np.timedelta64(365, "D"))
                    & (r_prev > 0) & (self.rung < self.top_rung))
        p = np.array([mc["promotion_prob_by_rating"][int(r)] if r > 0 else 0.0 for r in r_prev])
        u = self.rng.random(self.n)
        for i in np.flatnonzero(eligible & (u < p)):
            plan.append((promo_date, 1, "PROMOTION", i))

        # lateral moves: one at most per employee-year, 6+ months after hire
        active_y = (self.hire <= y1) & (np.isnat(self.exit) | (self.exit >= y0))
        w0 = np.maximum(y0, self.hire + np.timedelta64(180, "D"))
        w1 = np.where(np.isnat(self.exit), y1, np.minimum(y1, self.exit - np.timedelta64(1, "D")))
        span = np.where(active_y, (w1 - w0).astype(int) + 1, 0).clip(0)
        u = self.rng.random(self.n)
        off = (self.rng.random(self.n) * np.maximum(span, 1)).astype(int)
        lateral = (span > 0) & (u < mc["lateral_move_rate"] * span / 365)
        for i in np.flatnonzero(lateral):
            d = w0[i] + np.timedelta64(int(off[i]), "D")
            if d in reserved:
                d = d + np.timedelta64(1, "D") if d < w1[i] else d - np.timedelta64(1, "D")
            plan.append((d, 2, "TRANSFER", i))

        # internal requisition fills (seasonal like external hiring)
        taken = {e for *_x, e in plan}
        mid = np.datetime64(f"{y}-07-01")
        cand = np.flatnonzero(self._active_on(y1) & (self.hire <= mid - np.timedelta64(365, "D"))
                              & (r_prev >= 3) & ~np.isin(np.arange(self.n), list(taken)))
        k = min(len(cand), mc["internal_requisition_fills_per_year"])
        chosen = self.rng.choice(cand, size=k, replace=False)
        mw = self.cfg["hiring"]["month_weights"]
        months = self.rng.choice(sorted(mw), size=k, p=np.array([mw[m] for m in sorted(mw)]) / sum(mw.values()))
        for i, m in zip(chosen, months):
            d = np.datetime64(f"{y}-{m:02d}-01") + np.timedelta64(int(self.rng.integers(0, 28)), "D")
            if d in reserved:
                d += np.timedelta64(1, "D")
            plan.append((d, 3, "INTERNAL_HIRE", i))

        if y == reorg_date.astype("datetime64[Y]").astype(int) + 1970:
            plan.append((reorg_date, 0, "REORG", -1))

        grade_step = self.cfg["recruiting"]["internal_fill_grade_step"]
        for d, _o, kind, i in sorted(plan, key=lambda x: (x[0], x[1], x[3])):
            if kind == "REORG":
                dept = self.cfg["mobility"]["reorg"]["department"]
                for j in np.flatnonzero(self._active_on(d) & (self.hire < d)):   # hires that day join the new structure
                    if self.team_dept[self.team[j]] == dept:
                        self._record(j, d, "REORG", "Re-organisation")
                continue
            if not (self.hire[i] <= d and (np.isnat(self.exit[i]) or self.exit[i] > d)):
                continue
            if kind == "PROMOTION":
                if self.rung[i] < self.top_rung[i]:
                    self.rung[i] += 1
                    self._record(i, d, "PROMOTION", "Promotion")
            elif kind == "TRANSFER":
                tgt = self._target_team(i, prefer_other_dept=False)
                if tgt is not None:
                    self.team[i] = tgt
                    self._record(i, d, "TRANSFER", "Lateral move")
            else:
                tgt = self._target_team(i, prefer_other_dept=True)
                if tgt is None:
                    continue
                from_team, from_job = self.team[i], self._job(i)
                self.team[i] = tgt
                if self.rung[i] < self.top_rung[i] and self.rng.random() < grade_step:
                    self.rung[i] += 1
                ref = f"INT{len(self.internal_fills) + 1:04d}"
                self._record(i, d, "INTERNAL_HIRE", "Internal requisition", ref)
                self.internal_fills.append((i, d, tgt, self._job(i), from_team, from_job, ref))

    def _training(self, y: int):
        y0, y1 = _year_days(y)
        idx = np.flatnonzero((self.hire <= y1) & (np.isnat(self.exit) | (self.exit >= y0)))
        s = np.maximum(self.hire[idx], y0)
        e = np.where(np.isnat(self.exit[idx]), y1, np.minimum(self.exit[idx], y1))
        rows, h = self.trainer.year(y, idx, s, e, self.hire[idx], self.family[idx],
                                    self.archetype[idx], self.learn_z[idx])
        self.hours[y][idx] = h
        self.completions.extend(rows)

    def _reviews(self, y: int):
        _y0, y1 = _year_days(y)
        min_days = np.timedelta64(self.cfg["performance"]["min_tenure_days_for_rating"], "D")
        idx = np.flatnonzero(self._active_on(y1) & (self.hire <= y1 - min_days))
        self.rating[y][idx], self.potential[y][idx] = self.reviewer.draw(y, idx)

    def _terminations(self, y: int):
        ac = self.cfg["attrition"]
        y0, y1 = _year_days(y)
        for i in np.flatnonzero(~np.isnat(self.exit) & (self.exit >= y0) & (self.exit <= y1)):
            kind = self.exit_type[i]
            nd = ac["notice_days"][kind]
            if kind == "Voluntary" and (self.grade_no[(self.family[i], self.rung[i])] >= 9
                                        or self.family[i] == "Flight Deck"):
                nd = ac["notice_days_senior"]
            self.notice[i] = max(self.exit[i] - np.timedelta64(nd, "D"), self.hire[i])
            self._record(i, self.exit[i], "TERMINATION", kind)

    def run(self) -> "Simulation":
        self._opening_history()
        for y in self.years:
            self._snapshot_exits(y)
            self._new_hire_exits(y)
            self._moves(y)
            self._training(y)
            self._reviews(y)
            self._terminations(y)
        return self

    # --------------------------------------------------------------- outputs
    def job_history(self) -> pd.DataFrame:
        h = pd.DataFrame(self.history, columns=["i", "effective_date", "action_code", "action_reason",
                                                "team_code", "job_code", "requisition_ref"])
        h["emp_id"] = self.emp_id[h["i"]]
        term = h["action_code"] == "TERMINATION"
        h["term_type"] = np.where(term, h["action_reason"], None)
        h["regret_flag"] = np.where(term, np.where(self.regretted[h["i"]], "Y", "N"), None)
        h["notice_date"] = np.where(term, self.notice[h["i"]], NAT)
        h["effective_date"] = pd.to_datetime(h["effective_date"])
        h["notice_date"] = pd.to_datetime(h["notice_date"])
        h = h.sort_values(["emp_id", "effective_date", "action_code"]).reset_index(drop=True)
        return h[["emp_id", "effective_date", "action_code", "action_reason", "team_code", "job_code",
                  "requisition_ref", "term_type", "regret_flag", "notice_date"]]

    def reviews(self) -> pd.DataFrame:
        frames = []
        for y in self.years:
            idx = np.flatnonzero(self.rating[y] > 0)
            frames.append(pd.DataFrame({"emp_id": self.emp_id[idx], "review_year": y,
                                        "rating": self.rating[y][idx], "potential": self.potential[y][idx]}))
        return pd.concat(frames, ignore_index=True)

    def training_completions(self) -> pd.DataFrame:
        c = pd.DataFrame(self.completions, columns=["i", "course_code", "completion_date"])
        c["emp_id"] = self.emp_id[c["i"]]
        c["completion_date"] = pd.to_datetime(c["completion_date"])
        return c[["emp_id", "course_code", "completion_date"]]


def simulate(cfg: dict | None = None, pop: dict | None = None) -> Simulation:
    cfg = cfg or load_config()
    pop = pop or build_roster(cfg)
    return Simulation(cfg, pop).run()


if __name__ == "__main__":
    sim = simulate()
    h = sim.job_history()
    print(h["action_code"].value_counts().to_string())
