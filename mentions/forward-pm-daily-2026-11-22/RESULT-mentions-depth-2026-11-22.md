# Mentions (Polymarket 10c rule): depth, volume and $/day by family, 22 Nov 2026 (R-031 / R-033 / R-035)

Rule unchanged (frozen 10 Nov: per-word causal base rate, first-hour first BUY print, 10c edge, 5c-95c, hold to resolution, taker fee 0.04*p*(1-p)). Paper only.
Code: it/mentions_pm_depth_backtest.py (7 offline checks), it/mentions_pm_depth.py (5 checks), it/mentions_pm_firelog.py (9 checks) + cron scripts (tests 4 checks). Data: Gamma + data-api /v2/trades, pulled 22 Nov ~05:50Z. Files: this folder, depth_backtest_since_2026-01-01.json/.txt, print_and_book_depth_forward.json.

## A. FLOOR (print-based depth, NOT asks). Backtest 1 Jan - 22 Nov 2026 (325 days), $200 per trade, $2,000/day cap
Fill = all first-hour BUY prints on the rule's chosen token (own token, same market) with price <= q-10c (YES) or (1-q)-10c (NO), in time order, up to $200 notional. Resting asks that never printed are invisible, so this is a FLOOR on depth and on P&L.
| segment | events | bets | bets/day (calendar) | avg $ per bet | net $ | $/day | % of $200 | frozen rule (1 print) $/day |
|---|---|---|---|---|---|---|---|---|
| earnings-call | 126 | 29 | 0.09 | 12.59 | +414 | 1.27 | 0.64% | 0.96 |
| trump (events + weekly) | 294 | 109 | 0.34 | 15.04 | +703 | 2.16 | 1.08% | 2.35 |
| sports-announcers | 93 | 44 | 0.14 | 14.53 | +439 | 1.35 | 0.68% | 1.09 |
| other | 404 | 86 | 0.26 | 11.83 | +593 | 1.82 | 0.91% | 1.64 |
| ALL | 917 | 268 | 0.82 | 13.66 | +2,150 | 6.61 | 3.3% | 6.03 |
Reading: letting the bet take every qualifying first-hour print instead of the first one lifts $/day only 6.03 -> 6.61 and the average stays $12-15, so PRINTED depth at the rule's prices is thin ($200 never fills from prints: forward events 10 Nov-22 Nov, 0 of 17 had >= $200 of qualifying prints; since 2 Jul, 6 of 489, 1.2%). This does NOT say the asks were thin; it says nobody lifted them. Same-direction $200 sizing at the old +79% stake return (arithmetic only): about $94/day if depth existed.

## B. Volume per contract / event (all trades, all sides, price*size), same period
| segment | $ per event, median (all time) | $ per event, first 24 h, median | $ per contract, median / mean | $ per calendar day (mean) | $ per active day, median |
|---|---|---|---|---|---|
| earnings-call | 7,543 | 1,267 | 377 / 2,472 | 14,341 | 3,892 |
| trump | 29,854 | 4,584 | 1,212 / 6,493 | 125,550 | 31,276 |
| sports-announcers | 20,086 | 8,663 | 683 / 1,145 | 7,051 | 2,199 |
| other | 9,609 | 671 | 464 / 2,075 | 46,315 | 18,588 |
| ALL | 13,920 | 1,483 | 641 / 3,605 | 193,257 | 70,118 |
The $6-8K/day Nick quotes for earnings calls is consistent with the mean over active days of the biggest calls; the median earnings call is $7.5K over its whole life and $1.3K in its first 24 h. Most volume comes AFTER the first hour, where the frozen rule does not trade (audit s.6: 6 h and 24 h windows also pass at 10c, not tested here for capacity).

## C. MEASURED own-token asks (CLOB /book, both tokens, 22 Nov ~05:50Z) on 7 OPEN events: SNAPSHOT, not decision time
Dollars of asks at prices that keep the 10c edge now (q from the frozen causal history). Per event, best word-token and the number of word-tokens with any such ask:
Trump or Melania Thanksgiving (trump): best $240.71 (NO Xi/China), 9 tokens with depth, 3 above $189. Salesforce earnings call: best $216.82 (YES Data Center, best ask 0.108 vs q 0.83), 6 tokens. Deere earnings: best $46.55, 5 tokens. Dell earnings: best $35.55, 3 tokens. Trump Philippines: $16.40. Trump China APEC: $12.80. Caedrel Worlds stream: $0 (no asks).
So on a fresh-ish market some single tokens DO show $200+ of qualifying asks while printed first-hour depth is $12-15: depth can exceed print size. Whether that depth existed in the first hour, and how often, is NOT measured: these events are 3 to 22 days old except Thanksgiving (aged ~hours). The decision-time measurement needs the firelog (below).

## D. What is not done / next
1. Own-token ask ladders AT decision time: it/mentions_pm_firelog.py (cron */2 min, it/mentions_pm_firelog_cron.sh) logs both tokens' full ladders when the 10c rule fires on a mention event in its first hour, paper-fills at $200 (or the depth keeping edge >= 10c), $2,000/day cap, one paper bet per event, daily scoring. NOT RUNNING until IT installs it (IT row in it/00-URGENT-MENTIONS-install-firelog-R031.md). First data: next new mention market after install. Until then every figure above is FLOOR.
2. Reported number to quote: FLOOR 3.3% of $200 ($6.61/day over 1 Jan-22 Nov, 268 bets, 0.82 bets/day). No MEASURED $/day exists yet.
