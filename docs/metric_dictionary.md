# Metric dictionary

Every measure in the Power BI semantic model (`powerbi/PeopleAnalytics.SemanticModel`, table `_Measures`), nothing more and nothing less - `tests/test_semantic_model.py` fails if this file and the model drift apart.

Conventions

- Rates use `DIVIDE()`; a blank result means the denominator is zero or missing.
- Headcount and pay are **snapshots**: they read the last month end / latest pay review inside the selection.
- Flows (hires, exits, moves, applications, training) are **counted in the period** by their event date.
- ML measures read tables written by Python (`ml.*`); Power BI never fits a model.
- Driver measures describe **associations**, not causes.
- Sources are Postgres relations: `core.*` built by dbt, `ml.*` written by `ml/*.py`.

141 measures in 10 display folders.

| Folder | Measures |
|---|---|
| 01 Headcount | [Headcount End](#headcount-end), [Headcount Start](#headcount-start), [Headcount Avg](#headcount-avg), [Headcount FTE End](#headcount-fte-end), [FTE Avg](#fte-avg), [Headcount Change](#headcount-change), [Headcount Growth %](#headcount-growth-), [Hires](#hires), [Employees in Period](#employees-in-period), [Female Share of Headcount %](#female-share-of-headcount-), [Avg Tenure Years](#avg-tenure-years) |
| 02 Turnover | [Separations](#separations), [Voluntary Separations](#voluntary-separations), [Regretted Separations](#regretted-separations), [Turnover %](#turnover-), [Voluntary Turnover %](#voluntary-turnover-), [Regretted Turnover %](#regretted-turnover-), [Annualized Turnover %](#annualized-turnover-), [Regretted Share of Voluntary Exits %](#regretted-share-of-voluntary-exits-), [12M Retention %](#12m-retention-), [First-Year Attrition %](#first-year-attrition-), [Avg Tenure at Exit Months](#avg-tenure-at-exit-months), [Separations by Notice Date](#separations-by-notice-date) |
| 03 Recruiting | [Requisitions Opened](#requisitions-opened), [Requisitions Filled](#requisitions-filled), [Open Requisitions at Period End](#open-requisitions-at-period-end), [External Hires](#external-hires), [Internal Fills](#internal-fills), [Internal Fill Rate %](#internal-fill-rate-), [Avg Time to Fill Days](#avg-time-to-fill-days), [Avg Time to Start Days](#avg-time-to-start-days), [Recruiting Cost](#recruiting-cost), [Cost per Hire](#cost-per-hire), [External Cost per Hire](#external-cost-per-hire), [Backfill Rate Value](#backfill-rate-value), [True Internal Cost per Hire](#true-internal-cost-per-hire), [Hire 12M Exit Rate %](#hire-12m-exit-rate-) |
| 04 Funnel | [Applications](#applications), [Screened Applications](#screened-applications), [Interviewed Applications](#interviewed-applications), [Offers Made](#offers-made), [Offers Accepted](#offers-accepted), [Channel Yield %](#channel-yield-), [Offer Acceptance %](#offer-acceptance-), [Screen Rate %](#screen-rate-), [Interview Rate %](#interview-rate-), [Offer Rate %](#offer-rate-), [Applications per Hire](#applications-per-hire), [Applications Reaching Stage](#applications-reaching-stage), [Stage Conversion %](#stage-conversion-) |
| 05 Pay | [Latest Pay Review Date](#latest-pay-review-date), [Employees in Pay Review](#employees-in-pay-review), [Avg Base Salary](#avg-base-salary), [Median Base Salary](#median-base-salary), [Total Base Payroll](#total-base-payroll), [Avg Total Cash](#avg-total-cash), [Avg Compa-Ratio](#avg-compa-ratio), [Avg Range Penetration %](#avg-range-penetration-), [Below Band Minimum %](#below-band-minimum-), [Above Band Maximum %](#above-band-maximum-) |
| 06 Equity | [Avg Base Salary Female](#avg-base-salary-female), [Avg Base Salary Male](#avg-base-salary-male), [Raw Gap %](#raw-gap-), [Adjusted Gap %](#adjusted-gap-), [Adjusted Gap Without Performance %](#adjusted-gap-without-performance-), [Adjusted Gap CI Low %](#adjusted-gap-ci-low-), [Adjusted Gap CI High %](#adjusted-gap-ci-high-), [Adjusted Gap p-Value](#adjusted-gap-p-value), [Pay Model Effect %](#pay-model-effect-), [Pay Model p-Value](#pay-model-p-value), [Remediation Threshold Value](#remediation-threshold-value), [Employees Below Fair Pay](#employees-below-fair-pay), [Remediation Cost](#remediation-cost), [Female Share Below Fair Pay %](#female-share-below-fair-pay-), [Fair Pay Salary](#fair-pay-salary), [Actual Base Salary](#actual-base-salary), [Pay Std Residual](#pay-std-residual), [Is Below Fair Pay](#is-below-fair-pay), [Gap Closure Cost](#gap-closure-cost) |
| 07 Performance | [Employees Rated](#employees-rated), [Avg Performance Rating](#avg-performance-rating), [High Performer %](#high-performer-), [Low Performer %](#low-performer-), [Nine-Box Count](#nine-box-count), [Nine-Box Share %](#nine-box-share-), [Future Leaders Box 9](#future-leaders-box-9), [Promotions](#promotions), [Promotion %](#promotion-), [Internal Moves](#internal-moves), [Internal Mobility %](#internal-mobility-), [Reorg Moves](#reorg-moves), [All Moves Incl Reorg %](#all-moves-incl-reorg-) |
| 08 Training | [Training Hours](#training-hours), [Training Cost](#training-cost), [Courses Completed](#courses-completed), [Learners](#learners), [Training Participation %](#training-participation-), [Training Hours per FTE](#training-hours-per-fte), [Training Cost per FTE](#training-cost-per-fte), [Elective Training Hours](#elective-training-hours), [Over 20 Training Hours %](#over-20-training-hours-), [Voluntary Exit Rate Trained Over 20h %](#voluntary-exit-rate-trained-over-20h-), [Voluntary Exit Rate Trained 20h or Less %](#voluntary-exit-rate-trained-20h-or-less-), [Avoided Leavers Associated with Training](#avoided-leavers-associated-with-training), [Training ROI Proxy](#training-roi-proxy), [Segment Employees](#segment-employees), [Segment Avg Hours 24M](#segment-avg-hours-24m) |
| 09 Model quality | [Cutoff Value](#cutoff-value), [Leaver Cost Value](#leaver-cost-value), [Intervention Cost Value](#intervention-cost-value), [True Positives](#true-positives), [False Negatives](#false-negatives), [False Positives](#false-positives), [True Negatives](#true-negatives), [Recall %](#recall-), [Precision %](#precision-), [Flag Rate %](#flag-rate-), [Accuracy %](#accuracy-), [Expected Cost](#expected-cost), [Expected Cost Without Model](#expected-cost-without-model), [Expected Savings vs No Model](#expected-savings-vs-no-model), [AUC Test](#auc-test), [Base Rate Test %](#base-rate-test-), [Observed Leave Rate %](#observed-leave-rate-), [Avg Predicted Leave Probability %](#avg-predicted-leave-probability-), [Current At-Risk Employees](#current-at-risk-employees), [Current Avg Leave Probability %](#current-avg-leave-probability-), [Employee Leave Probability %](#employee-leave-probability-), [Is Flagged at Cutoff](#is-flagged-at-cutoff), [Driver Odds Ratio](#driver-odds-ratio), [Driver OR CI Low](#driver-or-ci-low), [Driver OR CI High](#driver-or-ci-high), [ROC True Positive Rate](#roc-true-positive-rate) |
| 10 Forecast | [Forecast Headcount](#forecast-headcount), [Forecast Headcount Lo80](#forecast-headcount-lo80), [Forecast Headcount Hi80](#forecast-headcount-hi80), [Backtest Forecast Headcount](#backtest-forecast-headcount), [Forecast vs Actual](#forecast-vs-actual), [Forecast vs Actual %](#forecast-vs-actual-), [MAPE Holdout %](#mape-holdout-), [Backtest MAPE Rolling Origin %](#backtest-mape-rolling-origin-) |

## 01 Headcount

### Headcount End

**Definition:** Employees on the payroll at the last month end in the selected period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_headcount_monthly rows at the last month_end in context |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _monthEnd = MAX ( 'Headcount'[month_end] )
RETURN
CALCULATE ( COUNTROWS ( 'Headcount' ), 'Headcount'[month_end] = _monthEnd )
```

### Headcount Start

**Definition:** Employees on the payroll at the month end before the selected period starts.

| Field | Value |
|---|---|
| Numerator / source | core.fact_headcount_monthly rows at the month_end before the period |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _previousMonthEnd = EOMONTH ( MIN ( 'Date'[date] ), -1 )
RETURN
CALCULATE ( COUNTROWS ( 'Headcount' ), REMOVEFILTERS ( 'Date' ), 'Headcount'[month_end] = _previousMonthEnd )
```

### Headcount Avg

**Definition:** Average of the month-end headcounts inside the selected period (denominator for rates).

| Field | Value |
|---|---|
| Numerator / source | Sum of month-end headcounts (core.fact_headcount_monthly) |
| Denominator | Number of month ends in the period |
| Owner | Workforce Planning Lead |
| Format | `#,0.0` |

```dax
AVERAGEX (
FILTER ( VALUES ( 'Date'[date] ), 'Date'[is_month_end] && 'Date'[is_in_reporting_window] ),
CALCULATE ( COUNTROWS ( 'Headcount' ) )
)
```

### Headcount FTE End

**Definition:** Full-time equivalents on the payroll at the last month end in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_headcount_monthly.fte at the last month_end |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0.0` |

```dax
VAR _monthEnd = MAX ( 'Headcount'[month_end] )
RETURN
CALCULATE ( SUM ( 'Headcount'[fte] ), 'Headcount'[month_end] = _monthEnd )
```

### FTE Avg

**Definition:** Average of the month-end FTE totals inside the selected period.

| Field | Value |
|---|---|
| Numerator / source | Sum of month-end FTE (core.fact_headcount_monthly.fte) |
| Denominator | Number of month ends in the period |
| Owner | Workforce Planning Lead |
| Format | `#,0.0` |

```dax
AVERAGEX (
FILTER ( VALUES ( 'Date'[date] ), 'Date'[is_month_end] && 'Date'[is_in_reporting_window] ),
CALCULATE ( SUM ( 'Headcount'[fte] ) )
)
```

### Headcount Change

**Definition:** Headcount End minus Headcount Start.

| Field | Value |
|---|---|
| Numerator / source | Headcount End |
| Denominator | Headcount Start (subtracted) |
| Owner | Workforce Planning Lead |
| Format | `+#,0;-#,0;0` |

```dax
[Headcount End] - [Headcount Start]
```

### Headcount Growth %

**Definition:** Change in headcount over the period relative to the starting headcount.

| Field | Value |
|---|---|
| Numerator / source | Headcount End - Headcount Start |
| Denominator | Headcount Start |
| Owner | Workforce Planning Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Headcount End] - [Headcount Start], [Headcount Start] )
```

### Hires

**Definition:** External hires with a hire date in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with event_type = Hire |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[event_type] = "Hire" )
```

### Employees in Period

**Definition:** Distinct employees on the payroll at any month end in the period.

| Field | Value |
|---|---|
| Numerator / source | Distinct emp_id in core.fact_headcount_monthly |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
DISTINCTCOUNT ( 'Headcount'[emp_id] )
```

### Female Share of Headcount %

**Definition:** Share of women in Headcount End.

| Field | Value |
|---|---|
| Numerator / source | Headcount End where core.dim_employee.gender = Female |
| Denominator | Headcount End |
| Owner | Workforce Planning Lead |
| Format | `0.0%` |

```dax
DIVIDE ( CALCULATE ( [Headcount End], 'Employee'[gender] = "Female" ), [Headcount End] )
```

### Avg Tenure Years

**Definition:** Average years of service of employees on the payroll at the last month end.

| Field | Value |
|---|---|
| Numerator / source | Average core.fact_headcount_monthly.tenure_months at the last month_end |
| Denominator | 12 months |
| Owner | Workforce Planning Lead |
| Format | `0.00` |

```dax
VAR _monthEnd = MAX ( 'Headcount'[month_end] )
RETURN
DIVIDE ( CALCULATE ( AVERAGE ( 'Headcount'[tenure_months] ), 'Headcount'[month_end] = _monthEnd ), 12 )
```

## 02 Turnover

### Separations

**Definition:** Exits of any type (voluntary, involuntary, retirement, transfer) with an exit date in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with event_type = Exit |
| Denominator | n/a |
| Owner | HR Business Partner Lead |
| Format | `#,0` |

```dax
CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[event_type] = "Exit" )
```

### Voluntary Separations

**Definition:** Resignations (exit_type = Voluntary) with an exit date in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event exits with exit_type = Voluntary |
| Denominator | n/a |
| Owner | HR Business Partner Lead |
| Format | `#,0` |

```dax
CALCULATE ( [Separations], 'Employee Event'[exit_type] = "Voluntary" )
```

### Regretted Separations

**Definition:** Voluntary exits flagged regretted (rating 4-5, potential 3 or critical role).

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event exits with is_regretted = true |
| Denominator | n/a |
| Owner | HR Business Partner Lead |
| Format | `#,0` |

```dax
CALCULATE ( [Separations], 'Employee Event'[is_regretted] = TRUE () )
```

### Turnover %

**Definition:** Separations divided by average headcount for the selected period (annual when a year is selected).

| Field | Value |
|---|---|
| Numerator / source | Separations |
| Denominator | Headcount Avg |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Separations], [Headcount Avg] )
```

### Voluntary Turnover %

**Definition:** Voluntary separations divided by average headcount for the selected period.

| Field | Value |
|---|---|
| Numerator / source | Voluntary Separations |
| Denominator | Headcount Avg |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Voluntary Separations], [Headcount Avg] )
```

### Regretted Turnover %

**Definition:** Regretted separations divided by average headcount for the selected period.

| Field | Value |
|---|---|
| Numerator / source | Regretted Separations |
| Denominator | Headcount Avg |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Regretted Separations], [Headcount Avg] )
```

### Annualized Turnover %

**Definition:** Turnover % scaled to 12 months so months, quarters and years compare.

| Field | Value |
|---|---|
| Numerator / source | Turnover % x 12 |
| Denominator | Number of month ends in the period |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
VAR _months = COUNTROWS ( FILTER ( VALUES ( 'Date'[date] ), 'Date'[is_month_end] && 'Date'[is_in_reporting_window] ) )
RETURN
DIVIDE ( [Turnover %] * 12, _months )
```

### Regretted Share of Voluntary Exits %

**Definition:** Share of resignations that were regretted.

| Field | Value |
|---|---|
| Numerator / source | Regretted Separations |
| Denominator | Voluntary Separations |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Regretted Separations], [Voluntary Separations] )
```

### 12M Retention %

**Definition:** Of the employees on the payroll 12 months before the period's last month end, the share still employed (anywhere in the company) at that month end.

| Field | Value |
|---|---|
| Numerator / source | Employees in the start cohort still in core.fact_headcount_monthly at the end month |
| Denominator | Employees in core.fact_headcount_monthly at end month - 12 |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
VAR _end = MAX ( 'Headcount'[month_end] )
VAR _start = EOMONTH ( _end, -12 )
VAR _cohort =
CALCULATETABLE ( VALUES ( 'Headcount'[emp_id] ), REMOVEFILTERS ( 'Date' ), 'Headcount'[month_end] = _start )
VAR _stillEmployed =
CALCULATETABLE (
VALUES ( 'Headcount'[emp_id] ),
REMOVEFILTERS ( 'Date' ),
REMOVEFILTERS ( 'Org Unit' ),
REMOVEFILTERS ( 'Job' ),
REMOVEFILTERS ( 'Location' ),
'Headcount'[month_end] = _end
)
RETURN
DIVIDE ( COUNTROWS ( INTERSECT ( _cohort, _stillEmployed ) ), COUNTROWS ( _cohort ) )
```

### First-Year Attrition %

**Definition:** Of the employees hired in the period, the share who left within 12 months of hire (any exit type). Recent cohorts are incomplete.

| Field | Value |
|---|---|
| Numerator / source | core.fact_separation rows with is_first_year_exit, filtered by hire_date (inactive relationship) |
| Denominator | Hires |
| Owner | HR Business Partner Lead |
| Format | `0.0%` |

```dax
VAR _firstYearExits =
CALCULATE (
COUNTROWS ( 'Separation' ),
USERELATIONSHIP ( 'Separation'[hire_date], 'Date'[date] ),
'Separation'[is_first_year_exit] = TRUE ()
)
RETURN
DIVIDE ( _firstYearExits, [Hires] )
```

### Avg Tenure at Exit Months

**Definition:** Average months of service of leavers in the period.

| Field | Value |
|---|---|
| Numerator / source | Average core.fact_separation.tenure_months |
| Denominator | n/a |
| Owner | HR Business Partner Lead |
| Format | `#,0.0` |

```dax
AVERAGE ( 'Separation'[tenure_months] )
```

### Separations by Notice Date

**Definition:** Exits counted by the date notice was given (leading indicator of exits).

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event exits filtered by notice_date (inactive relationship) |
| Denominator | n/a |
| Owner | HR Business Partner Lead |
| Format | `#,0` |

```dax
CALCULATE ( [Separations], USERELATIONSHIP ( 'Employee Event'[notice_date], 'Date'[date] ) )
```

## 03 Recruiting

### Requisitions Opened

**Definition:** Requisitions with an open date in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_requisition rows by open_date |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Requisition' )
```

### Requisitions Filled

**Definition:** Requisitions whose offer was accepted in the period (internal or external).

| Field | Value |
|---|---|
| Numerator / source | core.fact_requisition filled rows by accept_date (inactive relationship) |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
CALCULATE (
COUNTROWS ( 'Requisition' ),
'Requisition'[is_filled] = TRUE (),
USERELATIONSHIP ( 'Requisition'[accept_date], 'Date'[date] )
)
```

### Open Requisitions at Period End

**Definition:** Requisitions opened on or before the last day of the period and not yet closed on that day.

| Field | Value |
|---|---|
| Numerator / source | core.fact_requisition rows open on the last day of the period |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
VAR _end = MAX ( 'Date'[date] )
RETURN
CALCULATE (
COUNTROWS ( 'Requisition' ),
REMOVEFILTERS ( 'Date' ),
'Requisition'[open_date] <= _end,
ISBLANK ( 'Requisition'[closed_date] ) || 'Requisition'[closed_date] > _end
)
```

### External Hires

**Definition:** Requisitions filled by an external candidate who started in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_requisition rows with is_external_hire by start_date |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
CALCULATE (
COUNTROWS ( 'Requisition' ),
'Requisition'[is_external_hire] = TRUE (),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
```

### Internal Fills

**Definition:** Requisitions filled by an internal candidate who started in the new role in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_requisition rows with is_internal_fill by start_date |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
CALCULATE (
COUNTROWS ( 'Requisition' ),
'Requisition'[is_internal_fill] = TRUE (),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
```

### Internal Fill Rate %

**Definition:** Share of filled requisitions that went to internal candidates.

| Field | Value |
|---|---|
| Numerator / source | Internal Fills |
| Denominator | External Hires + Internal Fills |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Internal Fills], [External Hires] + [Internal Fills] )
```

### Avg Time to Fill Days

**Definition:** Average days from requisition open to offer accepted, for requisitions filled in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_requisition.days_to_fill (accept_date - open_date) |
| Denominator | Filled requisitions by accept_date |
| Owner | Talent Acquisition Lead |
| Format | `#,0.0` |

```dax
CALCULATE (
AVERAGE ( 'Requisition'[days_to_fill] ),
'Requisition'[is_filled] = TRUE (),
USERELATIONSHIP ( 'Requisition'[accept_date], 'Date'[date] )
)
```

### Avg Time to Start Days

**Definition:** Average days from requisition open to the hire's first day, for starts in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_requisition.days_to_start (start_date - open_date) |
| Denominator | Filled requisitions by start_date |
| Owner | Talent Acquisition Lead |
| Format | `#,0.0` |

```dax
CALCULATE (
AVERAGE ( 'Requisition'[days_to_start] ),
'Requisition'[is_filled] = TRUE (),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
```

### Recruiting Cost

**Definition:** External spend plus recruiter time for requisitions whose hire started in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_requisition.total_cost_usd (external + recruiter hours x hourly cost) |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `\$#,0` |

```dax
CALCULATE (
SUM ( 'Requisition'[total_cost_usd] ),
'Requisition'[is_filled] = TRUE (),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
```

### Cost per Hire

**Definition:** Recruiting cost divided by all hires (external hires and internal fills) starting in the period.

| Field | Value |
|---|---|
| Numerator / source | Recruiting Cost |
| Denominator | External Hires + Internal Fills |
| Owner | Talent Acquisition Lead |
| Format | `\$#,0` |

```dax
DIVIDE ( [Recruiting Cost], [External Hires] + [Internal Fills] )
```

### External Cost per Hire

**Definition:** Recruiting cost of external hires divided by external hires.

| Field | Value |
|---|---|
| Numerator / source | Recruiting Cost of external hires |
| Denominator | External Hires |
| Owner | Talent Acquisition Lead |
| Format | `\$#,0` |

```dax
DIVIDE ( CALCULATE ( [Recruiting Cost], 'Requisition'[is_external_hire] = TRUE () ), [External Hires] )
```

### Backfill Rate Value

**Definition:** Selected Backfill Rate what-if value (default 100%).

| Field | Value |
|---|---|
| Numerator / source | What-if table Backfill Rate |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `0%` |

```dax
SELECTEDVALUE ( 'Backfill Rate'[Backfill Rate], 1 )
```

### True Internal Cost per Hire

**Definition:** Direct cost of an internal fill plus the expected cost of backfilling the role the mover left: direct + Backfill Rate x External Cost per Hire.

| Field | Value |
|---|---|
| Numerator / source | Recruiting Cost of internal fills + Backfill Rate x External Cost per Hire x Internal Fills |
| Denominator | Internal Fills |
| Owner | Talent Acquisition Lead |
| Format | `\$#,0` |

```dax
VAR _direct = DIVIDE ( CALCULATE ( [Recruiting Cost], 'Requisition'[is_internal_fill] = TRUE () ), [Internal Fills] )
VAR _backfill = [Backfill Rate Value] * [External Cost per Hire]
RETURN
IF ( NOT ISBLANK ( _direct ), _direct + _backfill )
```

### Hire 12M Exit Rate %

**Definition:** Quality of hire: share of external hires starting in the period who left within 12 months (only hires with 12 months observable).

| Field | Value |
|---|---|
| Numerator / source | External hires with hire_exited_within_12m = true |
| Denominator | External hires with a non-null hire_exited_within_12m |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
VAR _left =
CALCULATE (
COUNTROWS ( 'Requisition' ),
'Requisition'[hire_exited_within_12m] = TRUE (),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
VAR _observable =
CALCULATE (
COUNTROWS ( 'Requisition' ),
NOT ISBLANK ( 'Requisition'[hire_exited_within_12m] ),
USERELATIONSHIP ( 'Requisition'[start_date], 'Date'[date] )
)
RETURN
DIVIDE ( _left, _observable )
```

## 04 Funnel

### Applications

**Definition:** Applications received in the period (by applied date).

| Field | Value |
|---|---|
| Numerator / source | core.fact_application rows |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Application' )
```

### Screened Applications

**Definition:** Applications that reached screening or later.

| Field | Value |
|---|---|
| Numerator / source | core.fact_application.reached_screen |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
SUM ( 'Application'[reached_screen] )
```

### Interviewed Applications

**Definition:** Applications that reached interview or later.

| Field | Value |
|---|---|
| Numerator / source | core.fact_application.reached_interview |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
SUM ( 'Application'[reached_interview] )
```

### Offers Made

**Definition:** Applications that received an offer (accepted or declined).

| Field | Value |
|---|---|
| Numerator / source | core.fact_application.reached_offer |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
SUM ( 'Application'[reached_offer] )
```

### Offers Accepted

**Definition:** Applications whose offer was accepted.

| Field | Value |
|---|---|
| Numerator / source | core.fact_application.accepted |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
SUM ( 'Application'[accepted] )
```

### Channel Yield %

**Definition:** Accepted offers divided by applications - the share of applicants from a channel who are hired.

| Field | Value |
|---|---|
| Numerator / source | Offers Accepted |
| Denominator | Applications |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Offers Accepted], [Applications] )
```

### Offer Acceptance %

**Definition:** Accepted offers divided by offers made.

| Field | Value |
|---|---|
| Numerator / source | Offers Accepted |
| Denominator | Offers Made |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Offers Accepted], [Offers Made] )
```

### Screen Rate %

**Definition:** Share of applications that reached screening.

| Field | Value |
|---|---|
| Numerator / source | Screened Applications |
| Denominator | Applications |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Screened Applications], [Applications] )
```

### Interview Rate %

**Definition:** Share of screened applications that reached interview.

| Field | Value |
|---|---|
| Numerator / source | Interviewed Applications |
| Denominator | Screened Applications |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Interviewed Applications], [Screened Applications] )
```

### Offer Rate %

**Definition:** Share of interviewed applications that received an offer.

| Field | Value |
|---|---|
| Numerator / source | Offers Made |
| Denominator | Interviewed Applications |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Offers Made], [Interviewed Applications] )
```

### Applications per Hire

**Definition:** Applications needed for one accepted offer.

| Field | Value |
|---|---|
| Numerator / source | Applications |
| Denominator | Offers Accepted |
| Owner | Talent Acquisition Lead |
| Format | `#,0.0` |

```dax
DIVIDE ( [Applications], [Offers Accepted] )
```

### Applications Reaching Stage

**Definition:** For the Funnel Stage on the axis, the applications that reached that stage or a later one.

| Field | Value |
|---|---|
| Numerator / source | core.fact_application rows with stage_reached >= selected stage |
| Denominator | n/a |
| Owner | Talent Acquisition Lead |
| Format | `#,0` |

```dax
VAR _stage = SELECTEDVALUE ( 'Funnel Stage'[stage_no] )
RETURN
IF ( NOT ISBLANK ( _stage ), CALCULATE ( COUNTROWS ( 'Application' ), 'Application'[stage_reached] >= _stage ) )
```

### Stage Conversion %

**Definition:** Applications reaching this stage divided by applications reaching the previous stage.

| Field | Value |
|---|---|
| Numerator / source | Applications Reaching Stage |
| Denominator | Applications reaching the previous stage |
| Owner | Talent Acquisition Lead |
| Format | `0.0%` |

```dax
VAR _stage = SELECTEDVALUE ( 'Funnel Stage'[stage_no] )
VAR _previous = CALCULATE ( COUNTROWS ( 'Application' ), 'Application'[stage_reached] >= _stage - 1 )
RETURN
IF ( _stage > 1, DIVIDE ( [Applications Reaching Stage], _previous ) )
```

## 05 Pay

### Latest Pay Review Date

**Definition:** The most recent annual pay review (1 April) inside the selection; pay measures use this snapshot.

| Field | Value |
|---|---|
| Numerator / source | Max core.fact_compensation.pay_review_date |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `yyyy-mm-dd` |

```dax
MAX ( 'Compensation'[pay_review_date] )
```

### Employees in Pay Review

**Definition:** Employees with a pay record at the latest pay review in the selection.

| Field | Value |
|---|---|
| Numerator / source | core.fact_compensation rows at the latest review |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `#,0` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( COUNTROWS ( 'Compensation' ), 'Compensation'[pay_review_date] = _review )
```

### Avg Base Salary

**Definition:** Average annual base salary at the latest pay review in the selection.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_compensation.base_salary at latest review |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( AVERAGE ( 'Compensation'[base_salary] ), 'Compensation'[pay_review_date] = _review )
```

### Median Base Salary

**Definition:** Median annual base salary at the latest pay review in the selection.

| Field | Value |
|---|---|
| Numerator / source | core.fact_compensation.base_salary at latest review |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( MEDIAN ( 'Compensation'[base_salary] ), 'Compensation'[pay_review_date] = _review )
```

### Total Base Payroll

**Definition:** Sum of annual base salaries at the latest pay review in the selection.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_compensation.base_salary at latest review |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( SUM ( 'Compensation'[base_salary] ), 'Compensation'[pay_review_date] = _review )
```

### Avg Total Cash

**Definition:** Average base plus allowances at the latest pay review in the selection.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_compensation.total_cash at latest review |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( AVERAGE ( 'Compensation'[total_cash] ), 'Compensation'[pay_review_date] = _review )
```

### Avg Compa-Ratio

**Definition:** Average of base salary / grade band midpoint at the latest pay review (1.00 = at midpoint).

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_compensation.compa_ratio (base_salary / band_mid) |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `0.000` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( AVERAGE ( 'Compensation'[compa_ratio] ), 'Compensation'[pay_review_date] = _review )
```

### Avg Range Penetration %

**Definition:** Average position of base salary in the band: 0% = band minimum, 100% = band maximum.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_compensation.range_penetration ((base - min) / (max - min)) |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
CALCULATE ( AVERAGE ( 'Compensation'[range_penetration] ), 'Compensation'[pay_review_date] = _review )
```

### Below Band Minimum %

**Definition:** Share of employees paid below their grade band minimum at the latest review.

| Field | Value |
|---|---|
| Numerator / source | Pay records with range_penetration < 0 |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
DIVIDE (
CALCULATE ( COUNTROWS ( 'Compensation' ), 'Compensation'[pay_review_date] = _review, 'Compensation'[range_penetration] < 0 ),
CALCULATE ( COUNTROWS ( 'Compensation' ), 'Compensation'[pay_review_date] = _review )
)
```

### Above Band Maximum %

**Definition:** Share of employees paid above their grade band maximum at the latest review.

| Field | Value |
|---|---|
| Numerator / source | Pay records with range_penetration > 1 |
| Denominator | Employees in Pay Review |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
VAR _review = MAX ( 'Compensation'[pay_review_date] )
RETURN
DIVIDE (
CALCULATE ( COUNTROWS ( 'Compensation' ), 'Compensation'[pay_review_date] = _review, 'Compensation'[range_penetration] > 1 ),
CALCULATE ( COUNTROWS ( 'Compensation' ), 'Compensation'[pay_review_date] = _review )
)
```

## 06 Equity

### Avg Base Salary Female

**Definition:** Average base salary of women at the latest pay review.

| Field | Value |
|---|---|
| Numerator / source | Avg Base Salary for gender = Female |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
CALCULATE ( [Avg Base Salary], 'Employee'[gender] = "Female" )
```

### Avg Base Salary Male

**Definition:** Average base salary of men at the latest pay review.

| Field | Value |
|---|---|
| Numerator / source | Avg Base Salary for gender = Male |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
CALCULATE ( [Avg Base Salary], 'Employee'[gender] = "Male" )
```

### Raw Gap %

**Definition:** Unadjusted gap: average female base / average male base - 1. Negative means women are paid less. No controls.

| Field | Value |
|---|---|
| Numerator / source | Avg Base Salary Female |
| Denominator | Avg Base Salary Male |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
VAR _female = [Avg Base Salary Female]
VAR _male = [Avg Base Salary Male]
RETURN
IF ( NOT ISBLANK ( _female ) && NOT ISBLANK ( _male ), DIVIDE ( _female, _male ) - 1 )
```

### Adjusted Gap %

**Definition:** Gender gap after grade, job family, tenure, station and performance: exp(coefficient on is_female) - 1 from the with_perf OLS model (company level, not sliceable).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.pct_effect (model with_perf, variable is_female) |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
CALCULATE (
MAX ( 'Pay Coefficient'[pct_effect] ),
'Pay Coefficient'[model] = "with_perf",
'Pay Coefficient'[variable] = "is_female"
)
```

### Adjusted Gap Without Performance %

**Definition:** Adjusted gap from the model that leaves performance rating out (tests whether ratings explain part of the gap).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.pct_effect (model without_perf, variable is_female) |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
CALCULATE (
MAX ( 'Pay Coefficient'[pct_effect] ),
'Pay Coefficient'[model] = "without_perf",
'Pay Coefficient'[variable] = "is_female"
)
```

### Adjusted Gap CI Low %

**Definition:** Lower bound of the 95% confidence interval of the adjusted gap.

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.ci_low (with_perf, is_female) |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
CALCULATE (
EXP ( MAX ( 'Pay Coefficient'[ci_low] ) ) - 1,
'Pay Coefficient'[model] = "with_perf",
'Pay Coefficient'[variable] = "is_female"
)
```

### Adjusted Gap CI High %

**Definition:** Upper bound of the 95% confidence interval of the adjusted gap.

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.ci_high (with_perf, is_female) |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
CALCULATE (
EXP ( MAX ( 'Pay Coefficient'[ci_high] ) ) - 1,
'Pay Coefficient'[model] = "with_perf",
'Pay Coefficient'[variable] = "is_female"
)
```

### Adjusted Gap p-Value

**Definition:** p-value of the gender coefficient in the with_perf model.

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.p_value (with_perf, is_female) |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0000` |

```dax
CALCULATE (
MAX ( 'Pay Coefficient'[p_value] ),
'Pay Coefficient'[model] = "with_perf",
'Pay Coefficient'[variable] = "is_female"
)
```

### Pay Model Effect %

**Definition:** Percentage effect exp(coef) - 1 of the pay-model variable on the visual (use with Pay Coefficient columns).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.pct_effect |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
MAX ( 'Pay Coefficient'[pct_effect] )
```

### Pay Model p-Value

**Definition:** p-value of the pay-model variable on the visual.

| Field | Value |
|---|---|
| Numerator / source | ml.pay_coefficients.p_value |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.0000` |

```dax
MAX ( 'Pay Coefficient'[p_value] )
```

### Remediation Threshold Value

**Definition:** Selected Remediation Threshold what-if value in standard deviations (default 1.5).

| Field | Value |
|---|---|
| Numerator / source | What-if table Remediation Threshold |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.00` |

```dax
SELECTEDVALUE ( 'Remediation Threshold'[Remediation Threshold], 1.5 )
```

### Employees Below Fair Pay

**Definition:** Employees whose standardised residual from the gender-blind fair-pay model is at or below minus the threshold.

| Field | Value |
|---|---|
| Numerator / source | ml.pay_residuals rows with std_resid <= -threshold |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `#,0` |

```dax
VAR _threshold = [Remediation Threshold Value]
RETURN
CALCULATE ( COUNTROWS ( 'Pay Residual' ), 'Pay Residual'[std_resid] <= -_threshold )
```

### Remediation Cost

**Definition:** Annual base cost of lifting every employee below fair pay to their predicted fair salary.

| Field | Value |
|---|---|
| Numerator / source | Sum of (pred_salary - base_salary) over ml.pay_residuals below the threshold |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _threshold = [Remediation Threshold Value]
RETURN
SUMX (
FILTER ( 'Pay Residual', 'Pay Residual'[std_resid] <= -_threshold ),
'Pay Residual'[pred_salary] - 'Pay Residual'[base_salary]
)
```

### Female Share Below Fair Pay %

**Definition:** Share of women among employees below fair pay.

| Field | Value |
|---|---|
| Numerator / source | Employees Below Fair Pay who are female |
| Denominator | Employees Below Fair Pay |
| Owner | Reward Lead |
| Format | `0.0%` |

```dax
DIVIDE ( CALCULATE ( [Employees Below Fair Pay], 'Pay Residual'[is_female] = 1 ), [Employees Below Fair Pay] )
```

### Fair Pay Salary

**Definition:** Predicted gender-blind fair salary of the employee on the visual (scatter X axis).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_residuals.pred_salary |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
MAX ( 'Pay Residual'[pred_salary] )
```

### Actual Base Salary

**Definition:** Actual base salary of the employee on the visual at the latest review (scatter Y axis).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_residuals.base_salary |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
MAX ( 'Pay Residual'[base_salary] )
```

### Pay Std Residual

**Definition:** Standardised residual from the fair-pay model for the employee on the visual (negative = paid below fair pay).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_residuals.std_resid |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0.00` |

```dax
MIN ( 'Pay Residual'[std_resid] )
```

### Is Below Fair Pay

**Definition:** 1 when the employee on the visual is at or below minus the remediation threshold, else 0 (use as a visual filter).

| Field | Value |
|---|---|
| Numerator / source | ml.pay_residuals.std_resid vs threshold |
| Denominator | n/a |
| Owner | Reward Lead |
| Format | `0` |

```dax
VAR _threshold = [Remediation Threshold Value]
RETURN
IF ( MIN ( 'Pay Residual'[std_resid] ) <= -_threshold, 1, 0 )
```

### Gap Closure Cost

**Definition:** Annual cost of raising all women's base pay by the adjusted gap: sum(female base) x (1 / (1 + gap) - 1).

| Field | Value |
|---|---|
| Numerator / source | Sum of female base in ml.pay_residuals x -gap |
| Denominator | 1 + Adjusted Gap % |
| Owner | Reward Lead |
| Format | `\$#,0` |

```dax
VAR _gap = [Adjusted Gap %]
VAR _femaleBase = CALCULATE ( SUM ( 'Pay Residual'[base_salary] ), 'Pay Residual'[is_female] = 1 )
RETURN
_femaleBase * DIVIDE ( -_gap, 1 + _gap )
```

## 07 Performance

### Employees Rated

**Definition:** Employees with a performance review in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_performance rows |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Performance' )
```

### Avg Performance Rating

**Definition:** Average rating (1-5) of reviews in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_performance.rating |
| Denominator | Employees Rated |
| Owner | Talent Management Lead |
| Format | `0.00` |

```dax
AVERAGE ( 'Performance'[rating] )
```

### High Performer %

**Definition:** Share of reviews rated 4 or 5.

| Field | Value |
|---|---|
| Numerator / source | Reviews with rating >= 4 |
| Denominator | Employees Rated |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE ( CALCULATE ( COUNTROWS ( 'Performance' ), 'Performance'[rating] >= 4 ), [Employees Rated] )
```

### Low Performer %

**Definition:** Share of reviews rated 1 or 2.

| Field | Value |
|---|---|
| Numerator / source | Reviews with rating <= 2 |
| Denominator | Employees Rated |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE ( CALCULATE ( COUNTROWS ( 'Performance' ), 'Performance'[rating] <= 2 ), [Employees Rated] )
```

### Nine-Box Count

**Definition:** Employees in each nine-box cell (performance band x potential) - use with the nine-box columns.

| Field | Value |
|---|---|
| Numerator / source | core.fact_performance rows per nine_box_cell |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Performance' )
```

### Nine-Box Share %

**Definition:** Share of rated employees in the nine-box cell on the visual.

| Field | Value |
|---|---|
| Numerator / source | Nine-Box Count |
| Denominator | Nine-Box Count across all cells |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE (
[Nine-Box Count],
CALCULATE (
[Nine-Box Count],
REMOVEFILTERS (
'Performance'[nine_box_cell],
'Performance'[nine_box_label],
'Performance'[performance_band],
'Performance'[potential]
)
)
)
```

### Future Leaders Box 9

**Definition:** Employees in nine-box cell 9 (high performance, high potential).

| Field | Value |
|---|---|
| Numerator / source | core.fact_performance rows with nine_box_cell = 9 |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
CALCULATE ( [Nine-Box Count], 'Performance'[nine_box_cell] = 9 )
```

### Promotions

**Definition:** Grade increases in the period (in-place promotions and internal moves to a higher grade).

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with is_promotion = true |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[is_promotion] = TRUE () )
```

### Promotion %

**Definition:** Promotions divided by average headcount.

| Field | Value |
|---|---|
| Numerator / source | Promotions |
| Denominator | Headcount Avg |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Promotions], [Headcount Avg] )
```

### Internal Moves

**Definition:** Lateral moves and internal requisition fills in the period. Excludes re-org moves.

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with move_type Lateral or Internal requisition |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[is_internal_mobility] = TRUE () )
```

### Internal Mobility %

**Definition:** Internal moves divided by average headcount (re-org moves excluded).

| Field | Value |
|---|---|
| Numerator / source | Internal Moves |
| Denominator | Headcount Avg |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Internal Moves], [Headcount Avg] )
```

### Reorg Moves

**Definition:** Org changes caused by the 2023 re-organisation (the employee did not choose to move).

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with move_type = Reorg |
| Denominator | n/a |
| Owner | Talent Management Lead |
| Format | `#,0` |

```dax
CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[move_type] = "Reorg" )
```

### All Moves Incl Reorg %

**Definition:** Every org move divided by average headcount - shows how the re-org inflates mobility if move_type is ignored.

| Field | Value |
|---|---|
| Numerator / source | core.fact_employee_event rows with event_type = Move |
| Denominator | Headcount Avg |
| Owner | Talent Management Lead |
| Format | `0.0%` |

```dax
DIVIDE ( CALCULATE ( COUNTROWS ( 'Employee Event' ), 'Employee Event'[event_type] = "Move" ), [Headcount Avg] )
```

## 08 Training

### Training Hours

**Definition:** Hours of training completed in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_training.hours |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0` |

```dax
SUM ( 'Training'[hours] )
```

### Training Cost

**Definition:** Cost of training completed in the period.

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_training.cost_usd |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `\$#,0` |

```dax
SUM ( 'Training'[cost_usd] )
```

### Courses Completed

**Definition:** Course completions in the period.

| Field | Value |
|---|---|
| Numerator / source | core.fact_training rows |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Training' )
```

### Learners

**Definition:** Distinct employees who completed at least one course in the period.

| Field | Value |
|---|---|
| Numerator / source | Distinct core.fact_training.emp_id |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0` |

```dax
DISTINCTCOUNT ( 'Training'[emp_id] )
```

### Training Participation %

**Definition:** Learners divided by employees on the payroll during the period.

| Field | Value |
|---|---|
| Numerator / source | Learners |
| Denominator | Employees in Period |
| Owner | Learning & Development Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Learners], [Employees in Period] )
```

### Training Hours per FTE

**Definition:** Training hours divided by average FTE.

| Field | Value |
|---|---|
| Numerator / source | Training Hours |
| Denominator | FTE Avg |
| Owner | Learning & Development Lead |
| Format | `#,0.0` |

```dax
DIVIDE ( [Training Hours], [FTE Avg] )
```

### Training Cost per FTE

**Definition:** Training cost divided by average FTE.

| Field | Value |
|---|---|
| Numerator / source | Training Cost |
| Denominator | FTE Avg |
| Owner | Learning & Development Lead |
| Format | `\$#,0` |

```dax
DIVIDE ( [Training Cost], [FTE Avg] )
```

### Elective Training Hours

**Definition:** Hours from elective courses (not mandatory, not onboarding).

| Field | Value |
|---|---|
| Numerator / source | Sum of core.fact_training.hours where program_type = Elective |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0` |

```dax
CALCULATE ( [Training Hours], 'Program'[program_type] = "Elective" )
```

### Over 20 Training Hours %

**Definition:** Share of snapshot employees who completed more than 20 training hours in the 12 months to the snapshot.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_scores rows with training_over_20h = 1 |
| Denominator | ml.attrition_scores rows |
| Owner | Learning & Development Lead |
| Format | `0.0%` |

```dax
DIVIDE (
CALCULATE ( COUNTROWS ( 'Attrition Score' ), 'Attrition Score'[training_over_20h] = 1 ),
COUNTROWS ( 'Attrition Score' )
)
```

### Voluntary Exit Rate Trained Over 20h %

**Definition:** 12-month voluntary exit rate of snapshot employees with more than 20 training hours (associated with, not caused by, training).

| Field | Value |
|---|---|
| Numerator / source | Snapshot employees with >20h who left voluntarily within 12 months |
| Denominator | Snapshot employees with >20h |
| Owner | Learning & Development Lead |
| Format | `0.0%` |

```dax
CALCULATE (
AVERAGE ( 'Attrition Score'[left_within_12m] ),
'Attrition Score'[training_over_20h] = 1,
'Attrition Score'[split] <> "current"
)
```

### Voluntary Exit Rate Trained 20h or Less %

**Definition:** 12-month voluntary exit rate of snapshot employees with 20 or fewer training hours.

| Field | Value |
|---|---|
| Numerator / source | Snapshot employees with <=20h who left voluntarily within 12 months |
| Denominator | Snapshot employees with <=20h |
| Owner | Learning & Development Lead |
| Format | `0.0%` |

```dax
CALCULATE (
AVERAGE ( 'Attrition Score'[left_within_12m] ),
'Attrition Score'[training_over_20h] = 0,
'Attrition Score'[split] <> "current"
)
```

### Avoided Leavers Associated with Training

**Definition:** Model-adjusted voluntary leavers associated with avoidance: for snapshot employees with >20 training hours, the sum of (probability without the training association - modelled probability), using the fitted odds ratio. Association, not causation.

| Field | Value |
|---|---|
| Numerator / source | Sum over ml.attrition_scores rows with training_over_20h = 1 of p(without) - p_leave; odds ratio from ml.attrition_coefficients |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0.0` |

```dax
VAR _oddsRatio =
CALCULATE ( MAX ( 'Attrition Coefficient'[odds_ratio] ), 'Attrition Coefficient'[variable] = "training_over_20h" )
RETURN
SUMX (
FILTER ( 'Attrition Score', 'Attrition Score'[training_over_20h] = 1 ),
VAR _p = 'Attrition Score'[p_leave]
VAR _oddsWithout = DIVIDE ( DIVIDE ( _p, 1 - _p ), _oddsRatio )
RETURN
DIVIDE ( _oddsWithout, 1 + _oddsWithout ) - _p
)
```

### Training ROI Proxy

**Definition:** (Avoided Leavers Associated with Training x Leaver Cost - Training Cost) / Training Cost for the selected period. A proxy built on an association, not a causal ROI.

| Field | Value |
|---|---|
| Numerator / source | Avoided Leavers Associated with Training x Leaver Cost - Training Cost |
| Denominator | Training Cost |
| Owner | Learning & Development Lead |
| Format | `0.0%` |

```dax
VAR _benefit = [Avoided Leavers Associated with Training] * [Leaver Cost Value]
VAR _cost = [Training Cost]
RETURN
DIVIDE ( _benefit - _cost, _cost )
```

### Segment Employees

**Definition:** Active employees in the learner segment on the visual (k-means, last 24 months).

| Field | Value |
|---|---|
| Numerator / source | ml.training_segments rows |
| Denominator | n/a |
| Owner | Learning & Development Lead |
| Format | `#,0` |

```dax
COUNTROWS ( 'Training Segment' )
```

### Segment Avg Hours 24M

**Definition:** Average training hours in the last 24 months for the learner segment on the visual.

| Field | Value |
|---|---|
| Numerator / source | Sum of ml.training_segments.total_hours |
| Denominator | Segment Employees |
| Owner | Learning & Development Lead |
| Format | `#,0.0` |

```dax
AVERAGE ( 'Training Segment'[total_hours] )
```

## 09 Model quality

### Cutoff Value

**Definition:** Selected Cutoff what-if value: employees with p_leave at or above it are flagged (default 15%).

| Field | Value |
|---|---|
| Numerator / source | What-if table Cutoff |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0%` |

```dax
SELECTEDVALUE ( 'Cutoff'[Cutoff], 0.15 )
```

### Leaver Cost Value

**Definition:** Selected Leaver Cost what-if value in USD (default 40,000).

| Field | Value |
|---|---|
| Numerator / source | What-if table Leaver Cost |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `\$#,0` |

```dax
SELECTEDVALUE ( 'Leaver Cost'[Leaver Cost], 40000 )
```

### Intervention Cost Value

**Definition:** Selected Intervention Cost what-if value in USD (default 3,000).

| Field | Value |
|---|---|
| Numerator / source | What-if table Intervention Cost |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `\$#,0` |

```dax
SELECTEDVALUE ( 'Intervention Cost'[Intervention Cost], 3000 )
```

### True Positives

**Definition:** Held-out snapshots flagged at the cutoff who did leave voluntarily within 12 months.

| Field | Value |
|---|---|
| Numerator / source | Test rows with p_leave >= cutoff and left_within_12m = 1 |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `#,0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
CALCULATE (
COUNTROWS ( 'Attrition Score' ),
'Attrition Score'[split] = "test",
'Attrition Score'[p_leave] >= _cutoff,
'Attrition Score'[left_within_12m] = 1
)
```

### False Negatives

**Definition:** Held-out snapshots not flagged at the cutoff who did leave.

| Field | Value |
|---|---|
| Numerator / source | Test rows with p_leave < cutoff and left_within_12m = 1 |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `#,0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
CALCULATE (
COUNTROWS ( 'Attrition Score' ),
'Attrition Score'[split] = "test",
'Attrition Score'[p_leave] < _cutoff,
'Attrition Score'[left_within_12m] = 1
)
```

### False Positives

**Definition:** Held-out snapshots flagged at the cutoff who stayed.

| Field | Value |
|---|---|
| Numerator / source | Test rows with p_leave >= cutoff and left_within_12m = 0 |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `#,0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
CALCULATE (
COUNTROWS ( 'Attrition Score' ),
'Attrition Score'[split] = "test",
'Attrition Score'[p_leave] >= _cutoff,
'Attrition Score'[left_within_12m] = 0
)
```

### True Negatives

**Definition:** Held-out snapshots not flagged at the cutoff who stayed.

| Field | Value |
|---|---|
| Numerator / source | Test rows with p_leave < cutoff and left_within_12m = 0 |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `#,0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
CALCULATE (
COUNTROWS ( 'Attrition Score' ),
'Attrition Score'[split] = "test",
'Attrition Score'[p_leave] < _cutoff,
'Attrition Score'[left_within_12m] = 0
)
```

### Recall %

**Definition:** Share of actual leavers the model flags at the cutoff: TP / (TP + FN).

| Field | Value |
|---|---|
| Numerator / source | True Positives |
| Denominator | True Positives + False Negatives |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [True Positives], [True Positives] + [False Negatives] )
```

### Precision %

**Definition:** Share of flagged employees who actually leave: TP / (TP + FP).

| Field | Value |
|---|---|
| Numerator / source | True Positives |
| Denominator | True Positives + False Positives |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [True Positives], [True Positives] + [False Positives] )
```

### Flag Rate %

**Definition:** Share of held-out snapshots flagged at the cutoff.

| Field | Value |
|---|---|
| Numerator / source | True Positives + False Positives |
| Denominator | All test rows |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
DIVIDE (
[True Positives] + [False Positives],
[True Positives] + [False Positives] + [False Negatives] + [True Negatives]
)
```

### Accuracy %

**Definition:** Share of held-out snapshots classified correctly at the cutoff.

| Field | Value |
|---|---|
| Numerator / source | True Positives + True Negatives |
| Denominator | All test rows |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
DIVIDE (
[True Positives] + [True Negatives],
[True Positives] + [False Positives] + [False Negatives] + [True Negatives]
)
```

### Expected Cost

**Definition:** Cost of acting at the cutoff on the test set: missed leavers x Leaver Cost + flagged employees x Intervention Cost (assumes an intervention retains a true positive).

| Field | Value |
|---|---|
| Numerator / source | False Negatives x Leaver Cost + (True Positives + False Positives) x Intervention Cost |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `\$#,0` |

```dax
[False Negatives] * [Leaver Cost Value]
+ ( [True Positives] + [False Positives] ) * [Intervention Cost Value]
```

### Expected Cost Without Model

**Definition:** Cost if nobody is flagged: every actual leaver costs the Leaver Cost.

| Field | Value |
|---|---|
| Numerator / source | Actual leavers x Leaver Cost |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `\$#,0` |

```dax
( [True Positives] + [False Negatives] ) * [Leaver Cost Value]
```

### Expected Savings vs No Model

**Definition:** Expected Cost Without Model minus Expected Cost at the selected cutoff.

| Field | Value |
|---|---|
| Numerator / source | Expected Cost Without Model |
| Denominator | Expected Cost (subtracted) |
| Owner | People Analytics Lead |
| Format | `\$#,0` |

```dax
[Expected Cost Without Model] - [Expected Cost]
```

### AUC Test

**Definition:** Area under the ROC curve on the held-out 30% of employees.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_metrics value for auc_test |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.000` |

```dax
CALCULATE ( MAX ( 'Attrition Metric'[value] ), 'Attrition Metric'[metric] = "auc_test" )
```

### Base Rate Test %

**Definition:** Voluntary 12-month exit rate in the held-out set.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_metrics value for base_rate_test |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
CALCULATE ( MAX ( 'Attrition Metric'[value] ), 'Attrition Metric'[metric] = "base_rate_test" )
```

### Observed Leave Rate %

**Definition:** Actual 12-month voluntary exit rate of held-out snapshots on the visual (calibration).

| Field | Value |
|---|---|
| Numerator / source | Test rows with left_within_12m = 1 |
| Denominator | Test rows |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
CALCULATE ( AVERAGE ( 'Attrition Score'[left_within_12m] ), 'Attrition Score'[split] = "test" )
```

### Avg Predicted Leave Probability %

**Definition:** Average predicted probability of held-out snapshots on the visual (calibration).

| Field | Value |
|---|---|
| Numerator / source | Sum of p_leave over test rows |
| Denominator | Test rows |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
CALCULATE ( AVERAGE ( 'Attrition Score'[p_leave] ), 'Attrition Score'[split] = "test" )
```

### Current At-Risk Employees

**Definition:** Employees at the latest snapshot (31-Dec-2025) whose predicted probability is at or above the cutoff.

| Field | Value |
|---|---|
| Numerator / source | Current-snapshot rows with p_leave >= cutoff |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `#,0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
CALCULATE (
COUNTROWS ( 'Attrition Score' ),
'Attrition Score'[split] = "current",
'Attrition Score'[p_leave] >= _cutoff
)
```

### Current Avg Leave Probability %

**Definition:** Average predicted 12-month voluntary exit probability at the latest snapshot.

| Field | Value |
|---|---|
| Numerator / source | Sum of p_leave over current rows |
| Denominator | Current rows |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
CALCULATE ( AVERAGE ( 'Attrition Score'[p_leave] ), 'Attrition Score'[split] = "current" )
```

### Employee Leave Probability %

**Definition:** Predicted 12-month voluntary exit probability of the employee snapshot on the visual.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_scores.p_leave |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.0%` |

```dax
MAX ( 'Attrition Score'[p_leave] )
```

### Is Flagged at Cutoff

**Definition:** 1 when the employee snapshot on the visual has p_leave at or above the cutoff, else 0 (use as a visual filter).

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_scores.p_leave vs Cutoff Value |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0` |

```dax
VAR _cutoff = [Cutoff Value]
RETURN
IF ( MAX ( 'Attrition Score'[p_leave] ) >= _cutoff, 1, 0 )
```

### Driver Odds Ratio

**Definition:** Odds ratio of the model variable on the visual (associated with leaving; 1 = no association).

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_coefficients.odds_ratio |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.00` |

```dax
MAX ( 'Attrition Coefficient'[odds_ratio] )
```

### Driver OR CI Low

**Definition:** Lower 95% bound of the odds ratio on the visual.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_coefficients.or_ci_low |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.00` |

```dax
MAX ( 'Attrition Coefficient'[or_ci_low] )
```

### Driver OR CI High

**Definition:** Upper 95% bound of the odds ratio on the visual.

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_coefficients.or_ci_high |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.00` |

```dax
MAX ( 'Attrition Coefficient'[or_ci_high] )
```

### ROC True Positive Rate

**Definition:** True positive rate for the false positive rate on the axis (ROC curve).

| Field | Value |
|---|---|
| Numerator / source | ml.attrition_roc.tpr |
| Denominator | n/a |
| Owner | People Analytics Lead |
| Format | `0.000` |

```dax
MAX ( 'Attrition ROC'[tpr] )
```

## 10 Forecast

### Forecast Headcount

**Definition:** Forecast headcount at the last forecast month in the selection (2026-2027).

| Field | Value |
|---|---|
| Numerator / source | Sum of ml.headcount_forecast.forecast (Forecast rows) at the last month |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _month = CALCULATE ( MAX ( 'Headcount Forecast'[month_end] ), 'Headcount Forecast'[row_type] = "Forecast" )
RETURN
CALCULATE (
SUM ( 'Headcount Forecast'[forecast] ),
'Headcount Forecast'[row_type] = "Forecast",
'Headcount Forecast'[month_end] = _month
)
```

### Forecast Headcount Lo80

**Definition:** Lower bound of the 80% prediction interval (summed across teams: conservative above division level).

| Field | Value |
|---|---|
| Numerator / source | Sum of ml.headcount_forecast.lo80 at the last month |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _month = CALCULATE ( MAX ( 'Headcount Forecast'[month_end] ), 'Headcount Forecast'[row_type] = "Forecast" )
RETURN
CALCULATE (
SUM ( 'Headcount Forecast'[lo80] ),
'Headcount Forecast'[row_type] = "Forecast",
'Headcount Forecast'[month_end] = _month
)
```

### Forecast Headcount Hi80

**Definition:** Upper bound of the 80% prediction interval (summed across teams: conservative above division level).

| Field | Value |
|---|---|
| Numerator / source | Sum of ml.headcount_forecast.hi80 at the last month |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _month = CALCULATE ( MAX ( 'Headcount Forecast'[month_end] ), 'Headcount Forecast'[row_type] = "Forecast" )
RETURN
CALCULATE (
SUM ( 'Headcount Forecast'[hi80] ),
'Headcount Forecast'[row_type] = "Forecast",
'Headcount Forecast'[month_end] = _month
)
```

### Backtest Forecast Headcount

**Definition:** Forecast made at 31-Dec-2023 for 2024-2025, at the last month in the selection (for forecast vs actual).

| Field | Value |
|---|---|
| Numerator / source | Sum of ml.headcount_forecast.forecast (Backtest rows) at the last month |
| Denominator | n/a |
| Owner | Workforce Planning Lead |
| Format | `#,0` |

```dax
VAR _month = CALCULATE ( MAX ( 'Headcount Forecast'[month_end] ), 'Headcount Forecast'[row_type] = "Backtest" )
RETURN
CALCULATE (
SUM ( 'Headcount Forecast'[forecast] ),
'Headcount Forecast'[row_type] = "Backtest",
'Headcount Forecast'[month_end] = _month
)
```

### Forecast vs Actual

**Definition:** Backtest forecast minus actual headcount at the same month end.

| Field | Value |
|---|---|
| Numerator / source | Backtest Forecast Headcount |
| Denominator | Headcount End (subtracted) |
| Owner | Workforce Planning Lead |
| Format | `+#,0;-#,0;0` |

```dax
[Backtest Forecast Headcount] - [Headcount End]
```

### Forecast vs Actual %

**Definition:** Backtest forecast error relative to actual headcount.

| Field | Value |
|---|---|
| Numerator / source | Backtest Forecast Headcount - Headcount End |
| Denominator | Headcount End |
| Owner | Workforce Planning Lead |
| Format | `0.0%` |

```dax
DIVIDE ( [Backtest Forecast Headcount] - [Headcount End], [Headcount End] )
```

### MAPE Holdout %

**Definition:** Mean absolute percentage error of the 2024-2025 backtest vs actual, over the month ends in the selection.

| Field | Value |
|---|---|
| Numerator / source | Sum of |backtest - actual| / actual per month end |
| Denominator | Month ends with a backtest and an actual |
| Owner | Workforce Planning Lead |
| Format | `0.00%` |

```dax
AVERAGEX (
FILTER ( VALUES ( 'Date'[date] ), 'Date'[is_month_end] ),
VAR _forecast = [Backtest Forecast Headcount]
VAR _actual = [Headcount End]
RETURN
IF ( NOT ISBLANK ( _forecast ) && NOT ISBLANK ( _actual ), DIVIDE ( ABS ( _forecast - _actual ), _actual ) )
)
```

### Backtest MAPE Rolling Origin %

**Definition:** Average rolling-origin backtest MAPE (25 origins, 2021-12..2023-12) over the forecast horizons in the selection; division-level when one division is in context, company-level otherwise.

| Field | Value |
|---|---|
| Numerator / source | ml.headcount_forecast.backtest_mape (percent) averaged over horizons |
| Denominator | 100 |
| Owner | Workforce Planning Lead |
| Format | `0.00%` |

```dax
VAR _oneDivision = DISTINCTCOUNT ( 'Org Unit'[current_division] ) = 1
VAR _mape =
CALCULATE (
AVERAGEX (
VALUES ( 'Headcount Forecast'[horizon_months] ),
IF (
_oneDivision,
CALCULATE ( MAX ( 'Headcount Forecast'[backtest_mape] ) ),
CALCULATE ( MAX ( 'Headcount Forecast'[backtest_mape_company] ) )
)
),
'Headcount Forecast'[row_type] = "Forecast"
)
RETURN
DIVIDE ( _mape, 100 )
```
