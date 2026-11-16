# Results: PM post-open drift on history, and commodity/FX/index perps vs the Sunday reopen (16 Nov 2026)
Rules: LOCKED-RULE-pm-postopen-2026-11-16.md and LOCKED-RULE-commodity-fx-reopen-2026-11-16.md (merged in PR #363 before any number). Scripts and raw cells: followups-2026-11-16/.

## 1. Polymarket post-open drift, trade-tape entry/exit, 8 bp round-trip fee
Entry = first taker trade in the signal direction in [T-29, T-20] min; exit = first opposite taker trade in [T+5, T+10] min. |S| >= 100 bp.
| | signals | with both trades | days | mean net (bp) | median net | 95% CI | % positive |
|---|---|---|---|---|---|---|---|
| Weekend, all | 266 | 90 | 13 | +35.3 | +22.1 | -22.5 to +95.7 | 58% |
| Weekend, index | | 12 | 7 | +143.5 | +45.1 | -4.2 to +300.2 | 67% |
| Weekend, equity | | 78 | 13 | +18.6 | +22.1 | -31.4 to +74.3 | 56% |
| Weekday placebo, all | 1139 | 309 | 55 | -27.1 | -20.3 | -61.9 to +7.1 | 43% |
Weekend minus weekday: +62 bp, CI -5.6 to +133. Largest single weekend = 40.3% of total net. 66% of weekend signals had no qualifying entry or exit trade (thin tape), median trade about $300 notional, median spread proxy 5 bp.
Locked rule outcome: NOT PASSED (CI lower bound below 0, difference CI includes 0, top weekend 40.3% > 40%). Unknown rather than disproved: only 13 weekends exist since PM went live. Roughly 7 signals with trades per weekend, so ~30 weekends (around Mar 2027) are needed, or a longer history from another venue. Capacity at this tape depth is a few hundred dollars per trade.

## 2. Commodity/FX perps vs the reopen, ranked by open interest (OI snapshot 16 Nov)
Weekday = median |hourly return difference| perp vs futures/FX (bp); gap = median |reopen - perp's weekend move| using the perp's own Friday close (a post-hoc variant: the locked version measured the perp LEVEL against the futures close and is dominated by the perp-futures basis, 50-140 bp for commodities, so I don't use it). FX volume is always 0 on Yahoo, so the zero-volume filter was applied only to symbols that report volume (mechanical fix, no outcome looked at).
| Perp | OI $m | weekday med / p90 | corr | weekend gap own-close | class |
|---|---|---|---|---|---|
| xyz BRENT | 299 | 4.5 / 15.8 | 0.69 | 54 | poor (corr) |
| xyz GOLD | 248 | 1.8 / 4.9 | 0.99 | 28 | tracks weekdays, gap poor |
| xyz CL | 132 | 2.5 / 7.7 | 0.97 | 46 | gap poor |
| xyz SILVER | 125 | 2.3 / 6.5 | 0.99 | 68 | gap poor |
| xyz JPY | 34 | 1.5 / 4.4 | 0.96 | 8 | good |
| xyz EUR | 31 | 1.5 / 4.1 | 0.92 | 4 | good |
| xyz NATGAS | 19 | 4.3 / 16.3 | 0.86 | 100 | poor |
| xyz COPPER | 6.7 | 3.5 / 9.7 | 0.97 | 40 | gap poor |
| PM GOLD | 6.2 | 4.2 / 13.8 | 0.87 | 29 | poor (corr) |
| xyz PLATINUM | 5.0 | 6.0 / 17.1 | 0.97 | 52 | gap poor |
| PM SILVER | 3.2 | 11.2 / 35.4 | 0.84 | 50 | poor |
| PM BRENT | 1.7 | 13.7 / 50.4 | 0.60 | 61 | poor |
| xyz PALLADIUM | 1.4 | 11.4 / 33.6 | 0.92 | 61 | gap poor |
| PM WTI | 1.3 | 9.9 / 31.2 | 0.90 | 32 | gap poor |
| xyz GBP | 0.4 | 3.3 / 10.1 | 0.44 | 17 | poor (corr) |
| flx (7 perps, OI ~0) | ~0 | 13-28 / 38-84 | 0.26-0.84 | 50-180 | poor |
No perp for CORN, WHEAT, ALUMINIUM, DXY (dropped). Spearman correlation OI vs weekday tracking error = -0.60 (n = 15): the smaller the open interest, the worse the tracking, which supports Nick's point. Even the big perps (gold, oil, silver) miss the Sunday reopen by 28-68 bp at the median, because the perp has been moving without the futures market.
Direction of the miss after the perp's weekend move (own close, |move| >= 50 bp, mean D = sign x (reopen - perp move), weekend-cluster 95% CI, n signals): Brent +48 [5, 95] (22, hit 100%); CL +21 [-21, 67] (20); silver -70 [-114, -27] (12); copper -56 [-94, -24] (13); platinum -104 [-156, -54] (10); natgas -59 [-118, 4] (16); palladium -46 [-90, 10] (13). So oil perps under-react (reopen goes further) while metals perps over-react (reopen falls back). Not a locked finding, post-hoc variant, CIs unadjusted for 7 looks; each would need its own locked forward rule. Gold n too small (4). FX: no |S| >= 50 bp weekends.
Limits: candle closes for the perp, Yahoo front-month futures for the reference, OI is a single snapshot, no spreads or fees modelled in part 2.
