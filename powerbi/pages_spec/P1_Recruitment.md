# P1 Recruitment

Audience: Talent Acquisition lead, HRBPs. Grain used: requisition (`Requisition`), application (`Application`).

## Page 1 - Recruiting overview
**Question:** Are we filling roles fast enough, and where is demand coming from?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Card row (5 cards) | `Requisitions Opened`, `Requisitions Filled`, `Open Requisitions at Period End`, `Avg Time to Fill Days`, `Offer Acceptance %` | - | Time to fill amber > 60, red > 75 |
| 2 | Line + clustered column | Axis `Date[year_month]`; columns `Requisitions Opened`; line `External Hires` | Year slicer | Sep-Nov columns in accent colour (hiring peak) |
| 3 | Bar | Axis `Org Unit[division]`; `Open Requisitions at Period End` | - | Data labels on |
| 4 | Matrix | Rows `Job[job_family]` > `Job[job_title]`; `Requisitions Filled`, `Avg Time to Fill Days`, `Avg Time to Start Days` | - | Background colour scale on time to fill (green-red) |

Slicers: standard + `Job[critical_role_flag]`.

## Page 2 - Funnel by channel
**Question:** Which channels convert applicants into hires, and where do candidates drop out?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Funnel | Category `Funnel Stage[stage_name]`; value `Applications Reaching Stage` | - | Show % of first stage |
| 2 | Table | Rows `Channel[channel]`; `Applications`, `Screen Rate %`, `Interview Rate %`, `Offer Rate %`, `Offer Acceptance %`, `Channel Yield %`, `Applications per Hire` | - | Data bars on `Channel Yield %` |
| 3 | Clustered bar | Axis `Channel[channel]`; `Channel Yield %` | - | Reference line = overall yield |
| 4 | Stacked column 100% | Axis `Date[year]`; legend `Channel[channel]`; `Offers Accepted` | - | - |

Slicers: standard + `Channel[channel_type]`.

## Page 3 - Cost and quality of hire
**Question:** What does a hire cost by channel, what does an internal move really cost, and do hires stay?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Cost per Hire`, `External Cost per Hire`, `True Internal Cost per Hire`, `Internal Fill Rate %` | - | - |
| 2 | Slider | `Backfill Rate[Backfill Rate]` (what-if, default 100%) | - | Caption: "share of internal moves whose old role is backfilled externally" |
| 3 | Clustered bar | Axis `Channel[channel]`; `External Cost per Hire` | Channel type = External | - |
| 4 | Column | Axis `Channel[channel]`; `Hire 12M Exit Rate %` | - | Red if > 25% |
| 5 | Text box | "Quality of hire = share of external hires who left within 12 months; hires after Dec-2024 are not yet observable." | - | - |

Slicers: standard.

## Hand-check (Excel)
1. `Applications`, calendar 2025.
2. `Channel Yield %` for LinkedIn, calendar 2025.
3. `Avg Time to Fill Days`, requisitions accepted in 2025.
