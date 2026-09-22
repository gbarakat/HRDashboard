"""Pay equity: three OLS models on log base salary at the latest pay review.

  without_perf : gender + grade + job family + tenure (linear spline, knot 15y) + station
  with_perf    : without_perf + prior-year rating (centred at 3) + not-yet-rated flag
  fair_pay     : with_perf minus gender -> gender-blind "fair" pay; residuals flag outliers

Adjusted gap % = exp(coef on is_female) - 1 from the with_perf model (all legitimate factors).
Writes ml.pay_coefficients and ml.pay_residuals.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from ml import CONFIG, banner, read, write

CONTROLS = "C(grade) + C(job_family) + tenure_to_15 + tenure_over_15 + C(station_code)"
FORMULAS = {
    "without_perf": f"log_base ~ is_female + {CONTROLS}",
    "with_perf": f"log_base ~ is_female + {CONTROLS} + rating_centred + not_rated",
    "fair_pay": f"log_base ~ {CONTROLS} + rating_centred + not_rated",
}
TOLERANCE_PP = 0.5


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["log_base"] = np.log(df["base_salary"].astype(float))
    t = df["tenure_years"].astype(float)
    df["tenure_to_15"] = np.minimum(t, 15.0)
    df["tenure_over_15"] = np.maximum(t - 15.0, 0.0)
    df["not_rated"] = df["prior_year_rating"].isna().astype(int)
    df["rating_centred"] = (df["prior_year_rating"].fillna(3) - 3).astype(float)
    return df


def fit_models(df: pd.DataFrame) -> dict:
    return {name: smf.ols(f, data=df).fit() for name, f in FORMULAS.items()}


def coefficient_table(models: dict, review_year: int) -> pd.DataFrame:
    rows = []
    for name, m in models.items():
        ci = m.conf_int()
        for var in m.params.index:
            rows.append({
                "model": name, "variable": var, "coef": m.params[var], "std_err": m.bse[var],
                "p_value": m.pvalues[var], "ci_low": ci.loc[var, 0], "ci_high": ci.loc[var, 1],
                "pct_effect": np.exp(m.params[var]) - 1, "n_obs": int(m.nobs), "r_squared": m.rsquared,
                "review_year": review_year})
    return pd.DataFrame(rows)


def residual_table(df: pd.DataFrame, fair) -> pd.DataFrame:
    smearing = np.mean(np.exp(fair.resid))           # Duan smearing: unbiased back-transform
    infl = fair.get_influence()
    return pd.DataFrame({
        "employee_key": df["employee_key"].astype(int), "emp_id": df["emp_id"],
        "org_unit_key": df["org_unit_key"].astype(int), "review_year": df["review_year"].astype(int),
        "is_female": df["is_female"].astype(int), "base_salary": df["base_salary"].astype(float),
        "pred_salary": np.round(np.exp(fair.fittedvalues) * smearing, 2),
        "std_resid": np.round(infl.resid_studentized_internal, 4)})


def main() -> dict:
    feats = read("select * from ml.feat_pay_equity")
    year = int(feats["review_year"].max())
    df = prepare(feats[feats["review_year"] == year]).reset_index(drop=True)
    models = fit_models(df)
    write(coefficient_table(models, year), "pay_coefficients")
    write(residual_table(df, models["fair_pay"]), "pay_residuals")

    planted = CONFIG["pay"]["planted_female_gap"] * 100
    female = df["is_female"] == 1
    raw = (df.loc[female, "base_salary"].mean() / df.loc[~female, "base_salary"].mean() - 1) * 100
    m = models["with_perf"]
    adj = (np.exp(m.params["is_female"]) - 1) * 100
    lo, hi = (np.exp(m.conf_int().loc["is_female"]) - 1) * 100
    no_perf = (np.exp(models["without_perf"].params["is_female"]) - 1) * 100
    ok = abs(adj - planted) <= TOLERANCE_PP
    banner(f"Pay equity, review {year} (n={int(m.nobs)})")
    print(f"raw gap (mean F / mean M - 1)          {raw:6.1f}%")
    print(f"adjusted gap, without performance      {no_perf:6.2f}%")
    print(f"adjusted gap, with performance         {adj:6.2f}%  95% CI [{lo:.2f}, {hi:.2f}]")
    print(f"planted {planted:.1f}% +/- {TOLERANCE_PP}  ->  {'RECOVERED' if ok else 'NOT RECOVERED'}")
    return {"adjusted_gap_pct": adj, "ci": (lo, hi), "planted_pct": planted, "recovered": ok}


if __name__ == "__main__":
    main()
