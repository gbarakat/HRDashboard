# P2 Forecasting (workforce planning)

Audience: Workforce Planning, Finance. Grain: `Headcount` (employee x month end), `Headcount Forecast` (team x month).

## Page 1 - Headcount trend
**Question:** How has headcount moved, and what drives the monthly change?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Headcount End`, `Headcount Change`, `Headcount Growth %`, `FTE Avg` | - | Growth green > 0, red < 0 |
| 2 | Line | Axis `Date[year_month]`; `Headcount End`; legend `Org Unit[current_division]` | 2018-2025 | - |
| 3 | Line and clustered column | Axis `Date[year]`; columns `Hires`, `Separations`; line `Headcount Change` | - | Hires accent, separations grey |
| 4 | Column | Axis `Date[month_short]`; `Hires` | All years | Sep-Nov highlighted (planted seasonality) |

Note: use `Org Unit[current_division]` for trends so the 2023 re-org does not look like a step change;
`Org Unit[division]` shows the structure as it was at the time.

## Page 2 - Forecast 2026-2027
**Question:** Where will headcount be in 24 months, and how uncertain is that?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Line | Axis `Date[year_month]` 2023-01..2027-12; `Headcount End` (actual), `Forecast Headcount`, `Forecast Headcount Lo80`, `Forecast Headcount Hi80` | - | Actual solid accent; forecast dashed; Lo/Hi as error band (Analytics pane) |
| 2 | Cards | `Forecast Headcount` (Dec-2027), `Backtest MAPE Rolling Origin %` | Date = 2027 | - |
| 3 | Matrix | Rows `Org Unit[current_division]`; columns `Date[year]` 2026, 2027; `Forecast Headcount` | - | - |
| 4 | Text box | "ETS (damped trend + 12-month seasonality) per division, allocated to teams by current share. Intervals are 80%; summed across teams above division level they are conservative." | - | - |

## Page 3 - Backtest accuracy
**Question:** How wrong was the model when we could check it?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Line | Axis `Date[year_month]` 2024-01..2025-12; `Headcount End`, `Backtest Forecast Headcount` | - | - |
| 2 | Column | Axis `Date[year_month]`; `Forecast vs Actual %` | 2024-2025 | Red if abs > 2% |
| 3 | Cards | `MAPE Holdout %`, `Backtest MAPE Rolling Origin %` | 2024-2025 | - |
| 4 | Line | Axis `Headcount Forecast[horizon_months]`; `Backtest MAPE Rolling Origin %` | Row type = Forecast | "MAPE by forecast month" |

## Hand-check (Excel)
1. `Headcount End` at 31-Dec-2025 (company).
2. `Forecast Headcount` at Dec-2027 (company).
3. `MAPE Holdout %` over 2024-2025 (company).
