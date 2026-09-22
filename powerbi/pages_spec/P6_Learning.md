# P6 Learning & Development

Audience: L&D lead, HRBPs. Grain: `Training` (employee x program x completion), `Training Segment`, `Attrition Score`.

## Page 1 - Training activity
**Question:** How much training do we deliver, to whom, and at what cost?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Cards | `Training Hours`, `Training Hours per FTE`, `Training Cost per FTE`, `Training Participation %`, `Courses Completed` | Year slicer | - |
| 2 | Stacked column | Axis `Date[year]`; legend `Program[program_type]`; `Training Hours` | - | Mandatory grey, onboarding light, elective accent |
| 3 | Bar | Axis `Program[category]`; `Training Hours` | - | - |
| 4 | Matrix | Rows `Job[job_family]`; `Training Hours per FTE`, `Elective Training Hours` | - | Data bars |

## Page 2 - Learner segments
**Question:** What kinds of learners do we have?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Donut | Legend `Training Segment[segment_label]`; `Segment Employees` | - | - |
| 2 | Table | Rows `Training Segment[segment_label]`; `Segment Employees`, `Segment Avg Hours 24M` | - | - |
| 3 | Stacked bar | Axis `Org Unit[division]`; legend `Training Segment[segment_label]`; `Segment Employees` | - | - |
| 4 | Text box | "k-means (ml/learner_segments.py) on each employee's elective mix and intensity over the last 24 months; k chosen by silhouette with a parsimony rule." | - | - |

## Page 3 - Training and retention (associated with)
Title on canvas: **"Training associated with retention"** - never "training reduces attrition".
**Question:** Is more training associated with fewer resignations, and what might that be worth?

| # | Visual | Fields / measures | Filters | Formatting |
|---|---|---|---|---|
| 1 | Clustered column | `Voluntary Exit Rate Trained Over 20h %`, `Voluntary Exit Rate Trained 20h or Less %` | - | Note: raw rates are confounded by tenure (new hires get onboarding hours) |
| 2 | Card | `Driver Odds Ratio` | Attrition Coefficient[variable] = training_over_20h | "Adjusted odds ratio" |
| 3 | Cards | `Avoided Leavers Associated with Training`, `Training Cost`, `Training ROI Proxy` | Year slicer | ROI red < 0 |
| 4 | Slider | `Leaver Cost[Leaver Cost]` | - | - |
| 5 | Text box | "Raw exit rates barely differ because new hires (high risk) receive 24 onboarding hours. After adjustment the odds ratio is about 0.6. ROI proxy uses the adjusted association and includes mandatory training cost." | - | - |

## Hand-check (Excel)
1. `Training Hours per FTE`, calendar 2025.
2. `Training Participation %`, calendar 2025.
3. `Voluntary Exit Rate Trained Over 20h %` and `Voluntary Exit Rate Trained 20h or Less %` (all labelled snapshots).
