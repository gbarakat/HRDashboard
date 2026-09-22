"""Generator contracts: population size, determinism, realism targets from config.yaml."""
import hashlib

import numpy as np
import pandas as pd

from generator.events import simulate
from generator.population import build_roster
from generator.recruiting import build_requisitions


def _digest(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()


def test_one_population_of_6000(sim, cfg):
    roster = sim.pop["roster"]
    assert roster["emp_id"].is_unique
    assert len(roster) == cfg["population"]["total_employees"] == 6000
    assert roster["is_opening"].sum() == cfg["population"]["opening_headcount"]


def test_same_seed_same_data(sim, cfg):
    again = simulate(cfg, build_roster(cfg))
    assert _digest(sim.job_history()) == _digest(again.job_history())
    assert _digest(sim.training_completions()) == _digest(again.training_completions())
    assert _digest(sim.reviews()) == _digest(again.reviews())


def test_hires_per_year_and_seasonal_peak(sim, cfg):
    h = sim.job_history()
    hires = h[(h["action_code"] == "HIRE") & (h["effective_date"].dt.year >= 2018)]
    per_year = hires.groupby(hires["effective_date"].dt.year).size()
    assert (per_year == cfg["hiring"]["hires_per_year"]).all()
    share_sep_nov = hires["effective_date"].dt.month.isin([9, 10, 11]).mean()
    assert 0.32 <= share_sep_nov <= 0.40          # planted 36% vs 25% if flat


def test_turnover_and_voluntary_share(sim):
    h = sim.job_history()
    hire = pd.Series(sim.hire.astype("datetime64[ns]"))
    exit_ = pd.Series(sim.exit.astype("datetime64[ns]"))
    rates, vol = [], []
    for y in sim.years:
        month_ends = pd.date_range(f"{y - 1}-12-31", f"{y}-12-31", freq="ME")
        avg_hc = np.mean([((hire <= d) & (exit_.isna() | (exit_ > d))).sum() for d in month_ends])
        exits = h[(h["action_code"] == "TERMINATION") & (h["effective_date"].dt.year == y)]
        rates.append(len(exits) / avg_hc)
        vol.append((exits["term_type"] == "Voluntary").mean())
    assert 0.13 <= np.mean(rates) <= 0.15          # ~14% annual turnover
    assert 0.74 <= np.mean(vol) <= 0.82            # ~78% of exits voluntary


def test_rating_distribution_and_potential_correlation(sim, cfg):
    r = sim.reviews()
    shares = r["rating"].value_counts(normalize=True).sort_index()
    target = pd.Series(cfg["performance"]["rating_distribution"]).sort_index()
    assert (shares - target).abs().max() < 0.015
    assert abs(np.corrcoef(r["rating"], r["potential"])[0, 1] - 0.30) < 0.03


def test_funnel_yields_by_channel(sim, cfg):
    _reqs, apps = build_requisitions(cfg, sim)
    names = {"INT": "Internal", "REF": "Referral", "LNK": "LinkedIn", "JBD": "Job board", "AGY": "Agency", "CMP": "Campus"}
    realised = apps.assign(hired=apps["furthest_stage"] == "HIRED").groupby("source_code")["hired"].mean()
    for code, rate in realised.items():
        assert abs(rate - cfg["recruiting"]["channel_yield"][names[code]]) < 0.015, code
