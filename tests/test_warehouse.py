"""Warehouse and model contracts, read from Postgres after `make dbt` and `make ml`."""
import numpy as np
import pandas as pd
import pytest

from ml import CONFIG, read


@pytest.fixture(scope="module")
def headcount():
    return read("select month_end, count(*) as hc from core.fact_headcount_monthly group by 1 order by 1")


def test_headcount_reconciles_every_month(headcount):
    flows = read("""
        select (date_trunc('month', event_date) + interval '1 month - 1 day')::date as month_end,
               count(*) filter (where event_type = 'Hire') as hires,
               count(*) filter (where event_type = 'Exit') as exits
        from core.fact_employee_event group by 1""")
    df = headcount.merge(flows, on="month_end", how="left").fillna(0)
    df["expected"] = df["hc"].shift(1) + df["hires"] - df["exits"]
    window = df.iloc[1:]
    assert len(window) == 96
    assert (window["expected"] == window["hc"]).all()


def test_headcount_independent_of_scd2(headcount):
    """Recount month-end headcount straight from person dates and compare with the fact."""
    p = read("select hire_date, exit_date from core.dim_employee where is_current")
    hire, exit_ = pd.to_datetime(p["hire_date"]), pd.to_datetime(p["exit_date"])
    for _, row in headcount.iterrows():
        d = pd.Timestamp(row["month_end"])
        assert ((hire <= d) & (exit_.isna() | (exit_ > d))).sum() == row["hc"]


def test_adjusted_pay_gap_recovered():
    c = read("select * from ml.pay_coefficients where model = 'with_perf' and variable = 'is_female'").iloc[0]
    planted = CONFIG["pay"]["planted_female_gap"] * 100
    assert abs(c["pct_effect"] * 100 - planted) <= 0.5


def test_attrition_odds_ratios_recovered():
    c = read("select variable, odds_ratio, or_ci_low, or_ci_high from ml.attrition_coefficients").set_index("variable")
    for var, planted in [("commute_over_30km", 1.8), ("training_over_20h", 0.6)]:
        row = c.loc[var]
        assert row["or_ci_low"] <= planted <= row["or_ci_high"], var
        assert abs(row["odds_ratio"] - planted) <= 0.25, var


def test_attrition_model_beats_chance():
    m = read("select metric, value from ml.attrition_metrics").set_index("metric")["value"]
    assert m["auc_test"] > 0.65


def test_hiring_seasonality_recovered():
    h = read("select extract(month from event_date)::int as m, count(*) as n from core.fact_employee_event "
             "where event_type = 'Hire' group by 1")
    assert set(h.nlargest(3, "n")["m"]) == {9, 10, 11}


def test_forecast_backtest_is_reasonable():
    f = read("select horizon_months, max(backtest_mape_company) as mape from ml.headcount_forecast "
             "where row_type = 'Forecast' group by 1 order by 1")
    assert len(f) == 24
    assert f["mape"].max() < 5.0


def test_every_ml_score_belongs_to_the_one_population():
    orphans = read("""select count(*) as n from ml.attrition_scores s
                      left join core.dim_employee e using (employee_key) where e.employee_key is null""")
    assert orphans["n"].iloc[0] == 0
    emp = read("select count(distinct emp_id) as n from core.dim_employee")
    assert emp["n"].iloc[0] == 6000
