"""`python -m ml`: fit every model in dependency order, then print the planted-effect scorecard.
Exits non-zero if a planted effect is not recovered, so `make ml` fails loudly."""
from __future__ import annotations

import sys

from ml import attrition, banner, forecast, learner_segments, pay_equity


def main() -> int:
    pay = pay_equity.main()
    seg = learner_segments.main()
    att = attrition.main()
    fc = forecast.main()
    c, t = att["commute_over_30km"], att["training_over_20h"]
    rows = [
        ("Adjusted gender pay gap", "-4.0% +/- 0.5",
         f"{pay['adjusted_gap_pct']:.2f}% [{pay['ci'][0]:.2f}, {pay['ci'][1]:.2f}]", pay["recovered"]),
        ("Attrition OR, commute > 30 km", "1.8",
         f"{c['odds_ratio']:.2f} [{c['ci'][0]:.2f}, {c['ci'][1]:.2f}]", c["recovered"]),
        ("Attrition OR, training > 20 h/yr", "0.6",
         f"{t['odds_ratio']:.2f} [{t['ci'][0]:.2f}, {t['ci'][1]:.2f}]", t["recovered"]),
        ("Hiring peak months", "Sep, Oct, Nov",
         ", ".join({9: "Sep", 10: "Oct", 11: "Nov"}.get(m, str(m)) for m in fc["top3_months"]), fc["recovered"]),
        ("Learner archetypes (k-means)", "5 planted", f"k={seg['k']}, ARI {seg['ari']:.2f}", seg["recovered"]),
    ]
    banner("PLANTED EFFECTS")
    print(f"{'effect':<34}{'planted':<16}{'recovered (95% CI)':<28}status")
    for name, planted, got, ok in rows:
        print(f"{name:<34}{planted:<16}{got:<28}{'PASS' if ok else 'FAIL'}")
    print(f"attrition model held-out AUC {att['auc']:.3f}; forecast mean MAPE {fc['mape_mean']:.2f}%")
    return 0 if all(r[3] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
