# Page specs

One file per dashboard. Each page lists the business question, every visual (type, fields, measures,
filters, conditional formatting), the slicers, and the three numbers to hand-check in Excel
(values and SQL in [`docs/validation.md`](../../docs/validation.md)).

| File | Report folder | Open with |
|---|---|---|
| [P1_Recruitment.md](P1_Recruitment.md) | `P1_Recruitment.Report` | `PeopleAnalytics.pbip` |
| [P2_Forecasting.md](P2_Forecasting.md) | `P2_Forecasting.Report` | `P2_Forecasting.pbip` |
| [P3_Talent.md](P3_Talent.md) | `P3_Talent.Report` | `P3_Talent.pbip` |
| [P4_PayEquity.md](P4_PayEquity.md) | `P4_PayEquity.Report` | `P4_PayEquity.pbip` |
| [P5_Attrition.md](P5_Attrition.md) | `P5_Attrition.Report` | `P5_Attrition.pbip` |
| [P6_Learning.md](P6_Learning.md) | `P6_Learning.Report` | `P6_Learning.pbip` |

Conventions for every page

- Canvas 1280 x 720, title top-left, "as of" card top-right, slicers in a left rail (200 px).
- Standard slicers unless stated: `Date[Calendar]` hierarchy (Year > Quarter > Month) or `Date[Fiscal]`,
  `Org Unit[division]`, `Location[station_name]`, `Job[job_family]`.
- Measures come only from `_Measures`; implicit measures are disabled in the model.
- Pages that show model drivers say "associated with" in the title and never "causes" / "drives".
- Colour: one accent for the focus series, grey for context; red/amber only for thresholds named below.
