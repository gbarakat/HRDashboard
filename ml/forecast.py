"""Headcount forecast: 24 months ahead by division, with a rolling-origin backtest.

  * history restated to the CURRENT org structure (the 2023 re-org would otherwise look like a
    step change in two divisions)
  * model per division: ETS, additive damped trend + additive 12-month seasonality (statsmodels)
  * rolling-origin backtest: origins 2021-12 .. 2023-12, horizons 1..24 -> MAPE by horizon month
  * top-down allocation to teams by their share of division headcount at the forecast origin
Writes ml.headcount_forecast: 'Forecast' rows (2026-01..2027-12) and 'Backtest' rows
(origin 2023-12, 2024-01..2025-12) for the forecast-vs-actual view.
Also prints the recovered hiring seasonality (planted Sep-Nov peak).
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

from ml import banner, read, write

HORIZON = 24
BACKTEST_ORIGINS = pd.date_range("2021-12-31", "2023-12-31", freq="ME")
HOLDOUT_ORIGIN = pd.Timestamp("2023-12-31")
PLANTED_PEAK = {9, 10, 11}


def fit_forecast(y: pd.Series, horizon: int, intervals: bool = False) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ETSModel(y.astype(float), error="add", trend="add", damped_trend=True,
                         seasonal="add", seasonal_periods=12).fit(disp=False)
        if not intervals:
            return pd.DataFrame({"forecast": np.asarray(model.forecast(horizon))})
        pred = model.get_prediction(start=len(y), end=len(y) + horizon - 1).summary_frame(alpha=0.20)
    return pd.DataFrame({"forecast": pred["mean"].to_numpy(), "lo80": pred["pi_lower"].to_numpy(),
                         "hi80": pred["pi_upper"].to_numpy()})


def backtest(series: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for origin in BACKTEST_ORIGINS:
        preds = {}
        for name, y in series.items():
            train = y[y.index <= origin]
            actual = y[y.index > origin].iloc[:HORIZON]
            f = fit_forecast(train, len(actual))["forecast"].to_numpy()
            preds[name] = (f, actual.to_numpy())
            for h, (fc, ac) in enumerate(zip(f, actual.to_numpy()), start=1):
                rows.append((name, origin, h, fc, ac))
        total_f = sum(p[0] for p in preds.values())
        total_a = sum(p[1] for p in preds.values())
        for h, (fc, ac) in enumerate(zip(total_f, total_a), start=1):
            rows.append(("Company", origin, h, fc, ac))
    bt = pd.DataFrame(rows, columns=["series", "origin", "horizon", "forecast", "actual"])
    bt["ape"] = (bt["forecast"] - bt["actual"]).abs() / bt["actual"] * 100
    return bt


def allocate(div_fc: pd.DataFrame, shares: pd.DataFrame, division: str) -> pd.DataFrame:
    s = shares[shares["current_division"] == division]
    out = div_fc.merge(s[["current_org_unit_key", "team_code", "share"]], how="cross")
    for c in ["forecast", "lo80", "hi80"]:
        out[c] = (out[c] * out["share"]).round(3)
    return out.drop(columns="share")


def team_shares(hc: pd.DataFrame, at: pd.Timestamp) -> pd.DataFrame:
    s = hc[hc["month_end"] == at].copy()
    s["share"] = s["headcount"] / s.groupby("current_division")["headcount"].transform("sum")
    return s[["current_division", "current_org_unit_key", "team_code", "share"]]


def seasonality(hires: pd.Series) -> pd.Series:
    by_month = hires.groupby(hires.index.month).mean()
    return (by_month / by_month.mean()).round(3)


def main() -> dict:
    hc = read("select * from ml.feat_headcount_series order by month_end")
    hc["month_end"] = pd.to_datetime(hc["month_end"])
    div = hc.groupby(["current_division", "month_end"])["headcount"].sum()
    series = {d: div.loc[d].asfreq("ME") for d in div.index.get_level_values(0).unique()}

    bt = backtest(series)
    mape = bt.groupby(["series", "horizon"])["ape"].mean().rename("mape").reset_index()
    mape_div = mape.set_index(["series", "horizon"])["mape"]

    frames = []
    last = max(s.index.max() for s in series.values())
    for row_type, origin in [("Forecast", last), ("Backtest", HOLDOUT_ORIGIN)]:
        shares = team_shares(hc, origin)
        for name, y in series.items():
            f = fit_forecast(y[y.index <= origin], HORIZON, intervals=True)
            f["month_end"] = pd.date_range(origin + pd.offsets.MonthEnd(1), periods=HORIZON, freq="ME")
            f["horizon_months"] = np.arange(1, HORIZON + 1)
            f["backtest_mape"] = [round(mape_div[(name, h)], 3) for h in f["horizon_months"]]
            f["backtest_mape_company"] = [round(mape_div[("Company", h)], 3) for h in f["horizon_months"]]
            a = allocate(f, shares, name)
            a["row_type"], a["origin_month"] = row_type, origin
            frames.append(a)
    out = pd.concat(frames, ignore_index=True).rename(columns={"current_org_unit_key": "org_unit_key"})
    out = out[["month_end", "org_unit_key", "team_code", "row_type", "origin_month", "horizon_months",
               "forecast", "lo80", "hi80", "backtest_mape", "backtest_mape_company"]]
    out["month_end"] = out["month_end"].dt.date
    out["origin_month"] = pd.to_datetime(out["origin_month"]).dt.date
    write(out, "headcount_forecast")

    hires = hc.groupby("month_end")["company_hires"].first().asfreq("ME")
    idx = seasonality(hires)
    top3 = set(idx.sort_values(ascending=False).index[:3])
    company = mape[mape["series"] == "Company"].set_index("horizon")["mape"]
    banner(f"Headcount forecast ({len(series)} divisions, {HORIZON} months, {len(BACKTEST_ORIGINS)} backtest origins)")
    print("company MAPE by horizon month (%):")
    for start in (1, 13):
        print("  " + "  ".join(f"h{h:>2}:{company[h]:4.2f}" for h in range(start, start + 12)))
    print(f"  mean over 24 months: {company.mean():.2f}%")
    fut = out[out["row_type"] == "Forecast"].groupby("month_end")[["forecast", "lo80", "hi80"]].sum()
    print(f"company headcount 2027-12: {fut['forecast'].iloc[-1]:.0f} (80% interval, summed {fut['lo80'].iloc[-1]:.0f}-{fut['hi80'].iloc[-1]:.0f})")
    ok = top3 == PLANTED_PEAK
    names = {m: pd.Timestamp(2000, m, 1).strftime("%b") for m in range(1, 13)}
    print("hiring seasonal index: " + " ".join(f"{names[m]} {v:.2f}" for m, v in idx.items()))
    print(f"top-3 hiring months: {', '.join(names[m] for m in sorted(top3))}  planted Sep-Nov  ->  "
          f"{'RECOVERED' if ok else 'NOT RECOVERED'}")
    return {"mape_mean": company.mean(), "top3_months": sorted(top3), "recovered": ok}


if __name__ == "__main__":
    main()
