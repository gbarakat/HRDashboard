# P3 Talent (performance, potential, mobility)

Audience: Talent Management, HRBPs. Grain: `Performance` (employee x review year), `Employee Event`.

## Page 1 - Performance distribution
**Question:** Is the rating distribution calibrated, and does it differ across the organisation?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Employees Rated`, `Avg Performance Rating`, `High Performer %`, `Low Performer %` | Year slicer | - |
| 2 | Column | Axis `Performance[rating]`; `Employees Rated` | - | Target distribution 5/15/45/25/10 as a text note |
| 3 | 100% stacked bar | Axis `Org Unit[division]`; legend `Performance[performance_band]`; `Employees Rated` | - | Low red, Moderate grey, High accent |
| 4 | Table | Rows `Employee[gender]`; `Avg Performance Rating`, `High Performer %` | - | - |

## Page 2 - Nine-box
**Question:** Where is our future leadership bench?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Matrix (3 x 3) | Rows `Performance[potential]` (descending); columns `Performance[performance_band]` (Low, Moderate, High); values `Nine-Box Count`, `Nine-Box Share %` | Single review year | Background: box 9 accent, boxes 1/4/7 amber |
| 2 | Card | `Future Leaders Box 9` | - | - |
| 3 | Bar | Axis `Performance[nine_box_label]` (sorted by cell); `Nine-Box Count` | - | - |
| 4 | Bar | Axis `Job[job_family]`; `Future Leaders Box 9` | - | - |

## Page 3 - Promotions and mobility
**Question:** Are people moving and growing, and why does move_type matter?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Promotion %`, `Internal Mobility %`, `All Moves Incl Reorg %` | Year slicer | - |
| 2 | Line | Axis `Date[year]`; `Internal Mobility %`, `All Moves Incl Reorg %` | 2018-2025 | Annotate 2023: "Airport Services re-org, 1-Jul-2023" |
| 3 | Column | Axis `Date[year]`; `Reorg Moves` | - | - |
| 4 | Clustered bar | Axis `Org Unit[division]`; `Promotion %`, `Internal Mobility %` | - | - |

## Hand-check (Excel)
1. `Employees Rated`, review year 2025.
2. `Nine-Box Count` for cell 9, review year 2025.
3. `High Performer %`, review year 2025.
