# P5 Attrition

Audience: HRBPs, CHRO. Grain: `Employee Event`, `Separation` (one row per exit), `Attrition Score` (employee x 31-Dec snapshot).

## Page 1 - Turnover overview
**Question:** How much are we losing, who, and when?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Turnover %`, `Voluntary Turnover %`, `Regretted Turnover %`, `12M Retention %`, `First-Year Attrition %` | Year slicer | Voluntary turnover red > 12% |
| 2 | Line | Axis `Date[year_month]`; `Annualized Turnover %` | - | Target line 14% |
| 3 | Column | Axis `Separation[tenure_band]` (sorted); `Separations` | Exit type = Voluntary | Months 3-12 bands highlighted |
| 4 | Donut | Legend `Employee Event[exit_type]`; `Separations` | - | - |
| 5 | Matrix | Rows `Org Unit[current_division]`; `Voluntary Turnover %`, `Regretted Separations`, `Avg Tenure at Exit Months` | - | Colour scale on turnover |

## Page 2 - Drivers (associated with)
Title on canvas: **"Factors associated with voluntary exit"** - never "causes".
**Question:** Which employee characteristics are associated with higher or lower odds of leaving?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Bar (forest-plot style) | Axis `Attrition Coefficient[variable]`; `Driver Odds Ratio`; error bars `Driver OR CI Low` / `Driver OR CI High` | Variable <> const | Reference line at 1.0; >1 red, <1 green |
| 2 | Column | Axis `Attrition Score[tenure_band]`; `Observed Leave Rate %` | Split = test | - |
| 3 | Clustered column | Axis `Attrition Score[commute_over_30km]`; `Observed Leave Rate %` | - | - |
| 4 | Text box | "Odds ratios from a logistic regression on 31-Dec snapshots (ml/attrition.py). They describe association after adjusting for the other factors; they are not causal effects." | - | - |

## Page 3 - Risk model and cutoff
**Question:** If we act on the model, how many leavers do we catch and at what cost?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Slider | `Cutoff[Cutoff]` (default 15%); `Leaver Cost[Leaver Cost]`; `Intervention Cost[Intervention Cost]` | - | - |
| 2 | Matrix 2 x 2 | Cards laid out as confusion matrix: `True Positives`, `False Negatives`, `False Positives`, `True Negatives` | - | TP/TN green, FN/FP red |
| 3 | Cards | `Recall %`, `Precision %`, `Flag Rate %`, `AUC Test`, `Expected Cost`, `Expected Savings vs No Model` | - | - |
| 4 | Line | Axis `Attrition ROC[fpr]`; `ROC True Positive Rate` | - | Diagonal reference |
| 5 | Clustered column | Axis `Attrition Score[decile]`; `Observed Leave Rate %`, `Avg Predicted Leave Probability %` | Split = test | Calibration check |
| 6 | Table | `Attrition Score[emp_id]`, `Org Unit[team_name]`; `Employee Leave Probability %` | `Attrition Score[split]` = current; visual filter `Is Flagged at Cutoff` = 1 | Top 50 by `Employee Leave Probability %` |

## Hand-check (Excel)
1. `Voluntary Turnover %`, calendar 2025.
2. `12M Retention %` at 31-Dec-2025.
3. `Recall %` at cutoff 15% (test split).
