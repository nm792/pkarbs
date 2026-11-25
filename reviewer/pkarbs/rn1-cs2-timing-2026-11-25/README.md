# RN1 CS2 taker timing vs public PandaScore events: status at 25 Nov 01:30Z (Reviewer)

## SETTLED (Nick, 24 Nov; rn1-recheck README section H, 181c996eb5)
- CS2 = a **fast-data TAKER edge**. After RN1 takes, the price keeps moving his way: +2.3c at 30 s, +2.5c at 60 s, +2.8c at 5 min (1,254 taker fills). To the result: +$115K on $956K, +12.0%, 73 matches, 95% CI -$45K to +$287K, so the interval includes zero.
- The **maker side is not a copyable rule** in CS2, Serie A or Ligue 1. Every 95% CI spans zero, and maker P&L is negative in all three once the top 5 markets are removed.
- Nick's order: "keep probing until we find something concrete". His working hypothesis: "he could simply be using GRID".

## Has the timing test run?
- **Yes, at 24 Nov 11:00Z** (owner thread P-PS-040; c3c9a7ea71, reviewer/pandascore/RESULT-rn1-vs-ps-events-2026-11-24.md). Result: **overlap 0.** The PandaScore capture covered 15 matches on 19-20 Nov, and RN1 made **0 taker fills** in them. His 73 CS2 taker matches (30 days) fall on days we did not capture. As a placebo, his maker fills showed no pattern either: 6 in the 10 s before an event vs 2 after; random times 5.6 vs 5.6.
- **Rerun now (25 Nov 01:30Z, this folder):** RN1's fills since 24 Nov 00:00Z, from /v2/trades with user= and taker_only=true/false, wallet asserted on every row (pull.py, rn1_cs2_fills_since_2026-11-24.json).
  - CS2 taker fills: **1**. At 2026-11-24T12:29:02Z: BUY 54.88 at 0.26, Liquid vs Wildcard BO1, PGL Major Singapore Stage 1 (cond 0x20121cfd6a...).
  - CS2 fills of any kind: 232 ($35.1K), between 11:28:49Z and 12:33:52Z, on two matches.
  - PandaScore raw hours on Prime for 24 Nov: 13Z, 14Z and 15Z only (IT P143 listing, 15:20Z). There is no 11Z or 12Z file. **Overlap with his taker fills is still 0.**

## What it needs and when
1. PandaScore capture running through his CS2 sessions. Nick approved v4 with watchdog at 01:17:07Z, and it is released to IT (trading-test reviewer IT-OPS-2026-11-25-0125Z). The PGL Major Singapore is under way now, which gives the most CS2 matches of the month.
2. Then this pull reruns every day. For each RN1 CS2 taker fill: time to the nearest PandaScore kill and round-end, before and after. Histogram -60..+60 s in 1 s bins, with his maker fills and random in-round times as placebo, as R-093 specified. The verdict is whether his takes land BEFORE public events (a faster feed, like GRID) or after them (fast reaction).
3. P151 (IT-OPS 0135Z) tests whether the public PandaScore feed itself leads Polymarket, on the 24 Nov 13-14Z hours.
