# P4 Pay Equity

Audience: Reward, CHRO. Grain: `Compensation` (employee x pay review), `Pay Coefficient`, `Pay Residual` (latest review).

## Page 1 - Pay structure
**Question:** Are people paid within their grade bands?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Latest Pay Review Date`, `Employees in Pay Review`, `Avg Compa-Ratio`, `Below Band Minimum %`, `Above Band Maximum %` | Year slicer | Compa-ratio amber outside 0.95-1.05 |
| 2 | Column | Axis `Job[grade]` (sorted by grade_no); `Avg Base Salary`, `Median Base Salary` | - | - |
| 3 | Matrix | Rows `Job[job_family]`; `Avg Compa-Ratio`, `Avg Range Penetration %` | - | Colour scale diverging at 1.00 / 50% |
| 4 | Bar | Axis `Location[station_name]`; `Avg Compa-Ratio` | - | - |

## Page 2 - Gender pay gap
**Question:** How big is the gap before and after legitimate factors?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Raw Gap %`, `Adjusted Gap %`, `Adjusted Gap CI Low %`, `Adjusted Gap CI High %`, `Adjusted Gap p-Value` | Year slicer (raw gap only) | - |
| 2 | Clustered bar | Axis `Job[job_family]`; `Avg Base Salary Female`, `Avg Base Salary Male` | - | Female accent, male grey |
| 3 | Table | `Pay Coefficient[model]`, `Pay Coefficient[variable]`; `Pay Model Effect %`, `Pay Model p-Value` | Variable = is_female | - |
| 4 | Text box | "Raw gap compares averages. Adjusted gap controls for grade, job family, tenure, station and performance (OLS on log base pay, `ml/pay_equity.py`). The adjusted gap is company-level and does not change with slicers." | - | - |

## Page 3 - Remediation
**Question:** Who is paid below fair pay, and what would it cost to fix?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Slider | `Remediation Threshold[Remediation Threshold]` (default 1.5 SD) | - | - |
| 2 | Cards | `Employees Below Fair Pay`, `Remediation Cost`, `Female Share Below Fair Pay %`, `Gap Closure Cost` | - | - |
| 3 | Scatter | Details `Pay Residual[emp_id]`; X `Fair Pay Salary`; Y `Actual Base Salary`; legend `Employee[gender]` | - | 45-degree reference line (y = x) |
| 4 | Table | `Pay Residual[emp_id]`, `Org Unit[team_name]`; `Actual Base Salary`, `Fair Pay Salary`, `Pay Std Residual` | Visual filter `Is Below Fair Pay` = 1 | Red icon when `Pay Std Residual` < -2 |

## Hand-check (Excel)
1. `Avg Compa-Ratio` at the 1-Apr-2025 review.
2. `Raw Gap %` at the 1-Apr-2025 review.
3. `Adjusted Gap %` (with_perf model) - compare with `ml.pay_coefficients`.
