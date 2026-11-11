# Step 1: which series have the winner emerge late (2026-11-11 04:30Z)
Universe: resolved events, >= $50k adj volume, excluding weather, 5-minute up/down, and everything already scanned in this project. PM = last 60d (top 1,500 events by volume), Kalshi = last 21d. No stats tests, no rules, no P&L.
'Late' = the eventual winner's price (YES for the winning bucket, or the winning side of a single contract) only STAYS above 50c after 70% of the market's life.


| # | series | volume $/day | resolved markets (events) | winners measured | share of winners emerging after 70% of life | mean emergence (fraction of life) | why (guess) |
|---|---|---:|---|---:|---:|---:|---|
| 1 | PM cat:soccer | $2,644,143 | 443 (100) | 13 | 54% | 0.59 | late data: in-play events decide it (goals, rounds, innings) |
| 2 | PM cat:premier-league | $1,642,036 | 431 (74) | 18 | 72% | 0.79 | late data: in-play events decide it (goals, rounds, innings) |
| 3 | PM cat:ucl | $1,240,438 | 467 (55) | 39 | 62% | 0.64 | late data: in-play events decide it (goals, rounds, innings) |
| 4 | PM cat:la-liga | $904,538 | 418 (49) | 17 | 59% | 0.64 | late data: in-play events decide it (goals, rounds, innings) |
| 5 | PM cat:mlb | $1,362,723 | 658 (63) | 9 | 22% | 0.20 | late data: in-play events decide it (goals, rounds, innings) |
| 6 | PM fc barcelona vs. real madrid cf | $147,843 | 16 (3) | 16 | 44% | 0.50 | late data: in-play events decide it (goals, rounds, innings) |
| 7 | PM cat:ligue-1 | $128,839 | 62 (10) | 28 | 46% | 0.60 | late data: in-play events decide it (goals, rounds, innings) |
| 8 | PM atlanta dream vs. golden state valkyries | $50,576 | 52 (3) | 25 | 100% | 0.98 | late data: price path decided near expiry (intraday/index-style) |
| 9 | PM cat:bundesliga | $218,619 | 115 (15) | 13 | 23% | 0.41 | late data: in-play events decide it (goals, rounds, innings) |
| 10 | PM cat:ufc | $94,774 | 43 (7) | 10 | 50% | 0.79 | late data: in-play events decide it (goals, rounds, innings) |
| 11 | PM club atlético de madrid vs. fc | $89,245 | 25 (4) | 25 | 52% | 0.62 | late data: in-play events decide it (goals, rounds, innings) |
| 12 | PM manchester city fc vs. brighton & | $43,706 | 6 (3) | 6 | 50% | 0.61 | late data: in-play events decide it (goals, rounds, innings) |
| 13 | PM cat:tech | $108,476 | 17 (5) | 16 | 19% | 0.26 | late data: scheduled release or announcement |
| 14 | PM tampa bay rays vs. cleveland guardians | $40,996 | 22 (3) | 11 | 45% | 0.46 | late data: in-play events decide it (goals, rounds, innings) |
| 15 | PM cat:finance | $125,331 | 25 (2) | 7 | 14% | 0.21 | late data: scheduled release or announcement |
| 16 | PM cat:geopolitics | $47,276 | 61 (3) | 32 | 31% | 0.36 | hard to model: news/political event flow |
| 17 | PM cat:mls | $26,521 | 15 (2) | 10 | 10% | 0.12 | late data: in-play events decide it (goals, rounds, innings) |

Ranked by volume x late share. Volume = event volume (PM gamma x0.5; Kalshi contracts x0.5), averaged over the window.

## Gas (exception to no-rescan, Nick 04:32Z) - Kalshi AAA gas series, last 60 days, same measure
Polymarket gas events are tiny (about $2-3k per daily event) and not measured.

| series | volume $/day | resolved winners (events) | measured | share after 70% | mean emergence |
| state daily (KXAAAGASD??) | $418,590 | 16942 (2289) | 32 | 0% | 0.06 |
| KXAAAGASD | $204,781 | 440 (59) | 35 | 6% | 0.08 |
| KXAAAGASW | $112,667 | 97 (9) | 40 | 0% | 0.10 |
| KXAAAGASM | $16,334 | 41 (2) | 39 | 0% | 0.01 |
| KXAAAGASMTX | $8,426 | 6 (2) | 5 | 40% | 0.37 |
| KXAAAGASWNJ | $4,871 | 76 (9) | 40 | 22% | 0.29 |
| KXAAAGASED | $3,665 | 9 (1) | 9 | 0% | 0.00 |
| KXAAAGASMINM | $3,588 | 9 (3) | 9 | 22% | 0.27 |
| KXAAAGASMAXM | $2,450 | 4 (2) | 4 | 50% | 0.66 |
