# Validation: three hand-checked numbers per dashboard

Each number below is computed three ways:
1. **SQL** against the warehouse (query below),
2. **Excel** from a CSV extract (steps below),
3. **Power BI** from the measure named in the page spec, using the stated filter.

All three must agree. The values are for the committed seed (42). Re-running `make all` reproduces them exactly.

## How to extract a CSV for Excel

```bash
docker exec pa_postgres psql -U pa -d people_analytics \
  -c "\copy (select * from core.fact_headcount_monthly where month_end between '2025-01-31' and '2025-12-31') to stdout csv header" \
  > headcount_2025.csv
```

Swap the table and filter for each check. Open the CSV in Excel and use a PivotTable (rows = the grouping,
values = Count or Average) or `COUNTIFS` / `AVERAGEIFS`.

## Values

| # | Dashboard | Measure (Power BI filter) | Expected |
|---|---|---|---|
| P1.1 | Recruitment | `Applications` (Year = 2025) | **7,350** |
| P1.2 | Recruitment | `Channel Yield %` (Year = 2025, Channel = LinkedIn) | **3.61%** |
| P1.3 | Recruitment | `Avg Time to Fill Days` (Year = 2025) | **54.9** |
| P2.1 | Forecasting | `Headcount End` (Year = 2025) | **2,876** |
| P2.2 | Forecasting | `Forecast Headcount` (Year = 2027) | **2,880** |
| P2.3 | Forecasting | `MAPE Holdout %` (Years 2024-2025) | **0.45%** |
| P3.1 | Talent | `Employees Rated` (Year = 2025) | **2,762** |
| P3.2 | Talent | `Nine-Box Count` (Year = 2025, nine_box_cell = 9) | **393** |
| P3.3 | Talent | `High Performer %` (Year = 2025) | **38.45%** |
| P4.1 | Pay Equity | `Avg Compa-Ratio` (Year = 2025) | **0.993** |
| P4.2 | Pay Equity | `Raw Gap %` (Year = 2025) | **-34.3%** |
| P4.3 | Pay Equity | `Adjusted Gap %` (no filter needed) | **-3.8%** |
| P5.1 | Attrition | `Voluntary Turnover %` (Year = 2025) | **10.44%** |
| P5.2 | Attrition | `12M Retention %` (Year = 2025) | **87.79%** |
| P5.3 | Attrition | `Recall %` (Cutoff = 15%) | **34.39%** |
| P6.1 | Learning | `Training Hours per FTE` (Year = 2025) | **26.27** |
| P6.2 | Learning | `Training Participation %` (Year = 2025) | **99.17%** |
| P6.3 | Learning | `Voluntary Exit Rate Trained Over 20h %` / `... 20h or Less %` (no filter) | **8.78% / 9.38%** |

Why P6.3 is interesting: the raw exit rates barely differ, yet the adjusted odds ratio for >20 training hours is
0.58 (planted 0.6). New hires are the highest-risk group and they receive 24 onboarding hours, so they sit in the
">20h" group and mask the association until tenure is controlled for. This is the confounding story the page tells.

## SQL to reproduce

```sql
-- P1.1 applications received in 2025
select count(*) from core.fact_application where extract(year from applied_date) = 2025;

-- P1.2 LinkedIn channel yield 2025 = accepted / applications
select round(100.0 * sum(a.accepted) / count(*), 2)
from core.fact_application a join core.dim_channel c using (channel_key)
where c.channel = 'LinkedIn' and extract(year from a.applied_date) = 2025;

-- P1.3 average days open -> offer accepted, requisitions accepted in 2025
select round(avg(days_to_fill), 1) from core.fact_requisition
where is_filled and extract(year from accept_date) = 2025;

-- P2.1 headcount at 31-Dec-2025
select count(*) from core.fact_headcount_monthly where month_end = '2025-12-31';

-- P2.2 company forecast for Dec-2027 (sum of team rows)
select round(sum(forecast)::numeric) from ml.headcount_forecast
where row_type = 'Forecast' and month_end = '2027-12-31';

-- P2.3 MAPE of the 2023-12 origin backtest vs actual, 2024-2025
select round((100 * avg(abs(f.fc - h.hc) / h.hc))::numeric, 3)
from (select month_end, sum(forecast) fc from ml.headcount_forecast where row_type = 'Backtest' group by 1) f
join (select month_end, count(*) hc from core.fact_headcount_monthly group by 1) h using (month_end);

-- P3.1 / P3.2 / P3.3
select count(*),
       count(*) filter (where nine_box_cell = 9),
       round(100.0 * avg((rating >= 4)::int), 2)
from core.fact_performance where review_year = 2025;

-- P4.1 / P4.2 at the 1-Apr-2025 review
select round(avg(c.compa_ratio), 4),
       round(100 * (avg(c.base_salary) filter (where e.gender = 'Female')
                  / avg(c.base_salary) filter (where e.gender = 'Male') - 1), 2)
from core.fact_compensation c join core.dim_employee e using (employee_key)
where c.pay_review_date = '2025-04-01';

-- P4.3 adjusted gap
select round(100 * pct_effect::numeric, 2) from ml.pay_coefficients
where model = 'with_perf' and variable = 'is_female';

-- P5.1 voluntary exits 2025 / average of the twelve 2025 month-end headcounts
select round(100.0 *
  (select count(*) from core.fact_employee_event where is_voluntary_exit and extract(year from event_date) = 2025) /
  (select avg(n) from (select month_end, count(*) n from core.fact_headcount_monthly
                       where month_end between '2025-01-31' and '2025-12-31' group by 1) x), 2);

-- P5.2 employees at 31-Dec-2024 still employed at 31-Dec-2025
select round(100.0 * count(b.emp_id) / count(*), 2)
from core.fact_headcount_monthly a
left join core.fact_headcount_monthly b on b.emp_id = a.emp_id and b.month_end = '2025-12-31'
where a.month_end = '2024-12-31';

-- P5.3 recall at cutoff 0.15 on the held-out test split
select round(100.0 * count(*) filter (where p_leave >= 0.15 and left_within_12m = 1)
                   / count(*) filter (where left_within_12m = 1), 2)
from ml.attrition_scores where split = 'test';

-- P6.1 training hours 2025 / average month-end FTE 2025
select round((select sum(hours) from core.fact_training where extract(year from completion_date) = 2025) /
             (select avg(f) from (select month_end, sum(fte) f from core.fact_headcount_monthly
                                  where month_end between '2025-01-31' and '2025-12-31' group by 1) x), 2);

-- P6.2 learners 2025 / employees on payroll at any 2025 month end
select round(100.0 * (select count(distinct emp_id) from core.fact_training where extract(year from completion_date) = 2025)
                   / (select count(distinct emp_id) from core.fact_headcount_monthly
                      where month_end between '2025-01-31' and '2025-12-31'), 2);

-- P6.3 12-month voluntary exit rate by training group (labelled snapshots)
select training_over_20h, round(100 * avg(left_within_12m)::numeric, 2)
from ml.attrition_scores where split <> 'current' group by 1;
```

## Excel recipes (one per number)

| # | Extract | Excel |
|---|---|---|
| P1.1 | `core.fact_application` where applied 2025 | Row count |
| P1.2 | same, joined to `core.dim_channel` | `=SUMIFS(accepted, channel,"LinkedIn") / COUNTIFS(channel,"LinkedIn")` |
| P1.3 | `core.fact_requisition` where is_filled and accept 2025 | `=AVERAGE(days_to_fill)` |
| P2.1 | `core.fact_headcount_monthly` month_end = 2025-12-31 | Row count |
| P2.2 | `ml.headcount_forecast` Forecast rows, 2027-12-31 | `=SUM(forecast)` |
| P2.3 | backtest rows + monthly headcount 2024-25 | Pivot by month, `=AVERAGE(ABS(fc-hc)/hc)` |
| P3.1-3 | `core.fact_performance` review_year = 2025 | Count; `COUNTIF(nine_box_cell,9)`; `COUNTIF(rating,">=4")/COUNT` |
| P4.1-2 | `core.fact_compensation` 2025-04-01 + gender | `=AVERAGE(compa_ratio)`; `=AVERAGEIF(gender,"Female",base)/AVERAGEIF(gender,"Male",base)-1` |
| P4.3 | `ml.pay_coefficients` | Read `pct_effect` for with_perf / is_female |
| P5.1 | exits 2025 + 12 month-end headcounts | voluntary exits / `AVERAGE` of the 12 monthly counts |
| P5.2 | headcount at 2024-12-31 and 2025-12-31 | `COUNTIF` of 2024 IDs found in 2025 / 2024 count |
| P5.3 | `ml.attrition_scores` split = test | `COUNTIFS(p_leave,">=0.15",left,1) / COUNTIF(left,1)` |
| P6.1 | 2025 training hours; 2025 monthly FTE | `SUM(hours) / AVERAGE(monthly FTE)` |
| P6.2 | 2025 training learners; 2025 headcount IDs | unique learners / unique employees |
| P6.3 | `ml.attrition_scores` split <> current | `AVERAGEIF(training_over_20h,1,left)` and `...,0,...` |

## Automated equivalents

- `dbt/tests/assert_headcount_reconciliation.sql`: headcount(m) = headcount(m-1) + hires - exits for all 96 months.
- `tests/test_warehouse.py`: the same reconciliation recomputed in pandas from person dates, plus planted-effect recovery.
- `tests/test_semantic_model.py`: every DAX reference resolves, ratios use `DIVIDE()`, dictionary == model.
