# Step 1: which series have the winner emerge late (2026-11-11 04:56Z)
Universe: resolved events, >= $50k adj volume, excluding weather, 5-minute up/down, and everything already scanned in this project. PM = last 60d (top 1,500 events by volume), Kalshi = last 21d. No stats tests, no rules, no P&L.
'Late' = the eventual winner's price (YES for the winning bucket, or the winning side of a single contract) only STAYS above 50c after 70% of the market's life.

NON-SPORTS ONLY (sports go to the faster-feed search). Kalshi window widened to 45 days.

Universe after filters: PM 13 events, Kalshi 330 events, 41 series.

### A. Late winners (ranked by volume x late share)
| # | series | volume $/day | resolved markets (events) | winners measured | late share (>70% of life) | mean emergence | why (guess) |
|---|---|---:|---|---:|---:|---:|---|
| 1 | PM cat:tech | $108,476 | 17 (5) | 16 | 19% | 0.26 | late data: scheduled release or announcement |
| 2 | PM cat:finance | $125,331 | 25 (2) | 7 | 14% | 0.21 | late data: scheduled release or announcement |
| 3 | PM cat:geopolitics | $47,276 | 61 (3) | 31 | 35% | 0.41 | hard to model: news/political event flow |
| 4 | K KXHOUSERACE | $28,480 | 10 (5) | 10 | 40% | 0.29 | unknown (read the market rules) |
| 5 | K KXINXU | $35,201 | 745 (12) | 39 | 13% | 0.11 | late data: price path decided near expiry (intraday/index-style) |
| 6 | K KXMIDTERMMOV | $8,430 | 20 (4) | 18 | 28% | 0.54 | hard to model: news/political event flow |
| 7 | K KXNASDAQ100U | $12,946 | 2051 (7) | 30 | 17% | 0.17 | late data: price path decided near expiry (intraday/index-style) |
| 8 | K KXWTI | $5,508 | 13 (2) | 13 | 31% | 0.29 | unknown (read the market rules) |
| 9 | K KXGOLDD | $5,030 | 51 (2) | 40 | 18% | 0.15 | late data: price path decided near expiry (intraday/index-style) |
| 10 | K KXSUEZWEEKLY | $2,056 | 6 (1) | 6 | 33% | 0.33 | unknown (read the market rules) |
| 11 | K KXHEGSETHMENTION | $1,615 | 15 (1) | 15 | 33% | 0.39 | late data: price path decided near expiry (intraday/index-style) |
| 12 | K KXDIESELD | $1,351 | 8 (1) | 8 | 12% | 0.11 | unknown (read the market rules) |
| 13 | K KXNATGASD | $1,379 | 92 (1) | 33 | 12% | 0.15 | unknown (read the market rules) |
| 14 | K KXYTVIEWSHIGH | $1,163 | 25 (1) | 25 | 4% | 0.12 | unknown (read the market rules) |

### B. Opposite pattern: early leader nearly always wins (winner above 50c within the first 10% of life), ranked by volume x early share
Flag only: whether buying the early leader pays depends on its price (see scan/gas_leader.py for the gas test).
| # | series | volume $/day | winners measured | early-leader share (<=10% of life) | mean emergence |
|---|---|---:|---:|---:|---:|
| 1 | PM cat:finance | $125,331 | 7 | 71% | 0.21 |
| 2 | PM cat:tech | $108,476 | 16 | 69% | 0.26 |
| 3 | K KXINXU | $35,201 | 39 | 87% | 0.11 |
| 4 | K KXHOUSERACE | $28,480 | 10 | 60% | 0.29 |
| 5 | PM cat:geopolitics | $47,276 | 31 | 26% | 0.41 |
| 6 | K KXNASDAQ100U | $12,946 | 30 | 80% | 0.17 |
| 7 | K KXGOLDD | $5,030 | 40 | 82% | 0.15 |
| 8 | K KXWTI | $5,508 | 13 | 69% | 0.29 |
| 9 | K KXMIDTERMMOV | $8,430 | 18 | 17% | 0.54 |
| 10 | K KXSUEZWEEKLY | $2,056 | 6 | 67% | 0.33 |
| 11 | K KXDIESELD | $1,351 | 8 | 88% | 0.11 |
| 12 | K KXNATGASD | $1,379 | 33 | 76% | 0.15 |
| 13 | K KXYTVIEWSHIGH | $1,163 | 25 | 68% | 0.12 |
| 14 | K KXHEGSETHMENTION | $1,615 | 15 | 40% | 0.39 |

Ranked by volume x late share. Volume = event volume (PM gamma x0.5; Kalshi contracts x0.5), averaged over the window.
