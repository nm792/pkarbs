# ADDENDUM to TASK-goalserve-trial-2026-11-12.md: in-play odds (Pinnacle) + rugby

Same start condition (/etc/pkarbs/goalserve.env). Read the CORRECTION section of feeds/NOTE-goalserve-trial-plan-2026-11-12.md.

Add to Part A:
- Rugby live scores to the poll list.
- IN-PLAY ODDS: if the key includes live odds, connect by WebSocket/push (else poll) and log every Pinnacle line update (bookmaker, sport, market, price, local recv ns). Record which sports actually have in-play odds and whether Pinnacle is live or pregame only.

Add to Part B (same locked rule, no changes after data):
- Odds signal lead = PM price-move onset minus Goalserve Pinnacle price-move onset (>=2c equivalent), judged by STANDARD-feed-latency-test.md v1 section 3 (benchmark = PM price; placebo-matched; n>=30; median real minus placebo >= +2.0 s; CI excludes 0; PM moves after the Pinnacle move in >=60% of events). Esports and tennis first (Pinnacle led PM there).
