# Volume-first scan 2026-11-11 02:42Z
Gate = $1,000,000/day conservative notional. PM gamma volume x0.5; Kalshi contracts x min(p,1-p). Weather + PM up/down excluded.

## STEP 1 - volume gate
| venue | unit | 24h $ (adj) | 7d avg $/day (adj) | gate value | pass |
|---|---|---:|---:|---:|---|
| PM | nba (31 events) | $6,861,085 | $1,314,394 | $1,314,394 | PASS |
| PM | fed (14 events) | $4,264,292 | $1,139,405 | $1,139,405 | PASS |
| PM | elections (206 events) | $2,900,971 | $4,638,105 | $2,900,971 | PASS |
| PM | politics (191 events) | $2,153,074 | $2,310,311 | $2,153,074 | PASS |
| PM | nhl (26 events) | $1,452,665 | $215,266 | $215,266 | no |
| PM | finance (59 events) | $1,334,333 | $634,561 | $634,561 | no |
| PM | bitcoin (22 events) | $1,103,899 | $590,849 | $590,849 | no |
| PM | cfb (37 events) | $1,102,077 | $179,679 | $179,679 | no |
| PM | esports (22 events) | $978,914 | $174,434 | $174,434 | no |
| PM | soccer (160 events) | $922,560 | $265,193 | $265,193 | no |
| PM | geopolitics (51 events) | $647,328 | $688,391 | $647,328 | no |
| PM | pop-culture (36 events) | $555,647 | $202,497 | $202,497 | no |
| PM | EXCL weather | $496,894 | $113,403 | - | excluded |
| PM | basketball (59 events) | $404,265 | $58,017 | $58,017 | no |
| PM | champions-league (2 events) | $393,842 | $361,949 | $361,949 | no |
| PM | nfl (73 events) | $364,999 | $139,188 | $139,188 | no |
| PM | ethereum (19 events) | $340,115 | $151,887 | $151,887 | no |
| PM | tech (91 events) | $306,916 | $146,381 | $146,381 | no |
| PM | EXCL crypto up/down | $20,242 | $2,896 | - | excluded |
| Kalshi | league:NBA [Sports] (4201 mkts) | $10,865,315 | n/a | $10,865,315 | PASS |
| Kalshi | league:NCAAF [Sports] (1899 mkts) | $3,983,507 | n/a | $3,983,507 | PASS |
| Kalshi | league:NFL [Sports] (2493 mkts) | $2,915,441 | n/a | $2,915,441 | PASS |
| Kalshi | league:NCAAMB [Sports] (1186 mkts) | $2,146,862 | n/a | $2,146,862 | PASS |
| Kalshi | league:NHL [Sports] (1421 mkts) | $1,029,153 | n/a | $1,029,153 | PASS |
| Kalshi | KXITFWMATCH [Sports] (158 mkts) | $379,204 | n/a | $379,204 | no |
| Kalshi | KXFEDDECISION [Economics] (28 mkts) | $369,394 | n/a | $369,394 | no |
| Kalshi | KXBTCD [Crypto] (95 mkts) | $319,465 | n/a | $319,465 | no |

Passed gate: 9 units. Categories under the floor are dropped, no estimates for them.

## STEP 2 - candidate rules on gated units only (9 units x 6 rules = 54 tests; Bonferroni alpha 0.05/54)
- K league:NBA: 150 resolved markets sampled (>= $25,000 each), 149 with usable price paths
- K league:NCAAF: 150 resolved markets sampled (>= $25,000 each), 146 with usable price paths
- K league:NFL: 150 resolved markets sampled (>= $25,000 each), 147 with usable price paths
- PM elections: 150 resolved markets sampled (>= $25,000 each), 149 with usable price paths
- PM politics: 150 resolved markets sampled (>= $25,000 each), 120 with usable price paths
- K league:NCAAMB: 150 resolved markets sampled (>= $25,000 each), 150 with usable price paths
- PM nba: 150 resolved markets sampled (>= $25,000 each), 146 with usable price paths
- PM fed: 21 resolved markets sampled (>= $25,000 each), 6 with usable price paths
- K league:NHL: 150 resolved markets sampled (>= $25,000 each), 149 with usable price paths

## RESULT - ranked by capturable $/day (PASS only; otherwise $0)
| # | unit | rule | unit $/day | n obs | markets | train net/$ | TEST net/$ | TEST lo95 | placebo z (need) | top3 | verdict | capturable $/day |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| 1 | PM nba | MOVE_fade | $1,314,394 | 43 | 43 | +57.6% | +87.6% | +39.4% | +3.2 (3.1) | 42% | PASS | $1,016 |
| 2 | K league:NCAAMB | FAV_fade | $2,146,862 | 61 | 24 | +221.3% | +80.5% | -106.2% | +1.5 (3.1) | 211% | FAIL | $0 |
| 3 | K league:NFL | LS_buy | $2,915,441 | 57 | 21 | -11.8% | +100.4% | -106.6% | +1.5 (3.1) | 177% | FAIL | $0 |
| 4 | K league:NBA | MOVE_fade | $10,865,315 | 60 | 60 | -28.8% | +33.2% | -62.1% | +1.3 (3.1) | 261% | FAIL | $0 |
| 5 | PM elections | LS_fade | $2,900,971 | 68 | 30 | +3.5% | +3.7% | +2.9% | +1.2 (3.1) | 39% | FAIL | $0 |
| 6 | K league:NCAAMB | LS_fade | $2,146,862 | 57 | 24 | +4.1% | +3.8% | +3.0% | +1.1 (3.1) | 39% | FAIL | $0 |
| 7 | PM elections | FAV_buy | $2,900,971 | 63 | 25 | +3.4% | +2.0% | -6.2% | +0.5 (3.1) | 107% | FAIL | $0 |
| 8 | K league:NBA | MOVE_follow | $10,865,315 | 60 | 60 | -13.0% | +0.8% | -23.5% | +0.2 (3.1) | 1185% | FAIL | $0 |
| 9 | K league:NCAAMB | MOVE_fade | $2,146,862 | 67 | 67 | -28.4% | +0.1% | -34.1% | +0.2 (3.1) | 29662% | FAIL | $0 |
| 10 | PM politics | MOVE_follow | $2,153,074 | 52 | 52 | -8.3% | +1.9% | -44.7% | +0.1 (3.1) | 1032% | FAIL | $0 |
| 11 | PM politics | LS_fade | $2,153,074 | 53 | 30 | +4.0% | +0.3% | -3.6% | +0.1 (3.1) | 682% | FAIL | $0 |
| 12 | PM politics | MOVE_fade | $2,153,074 | 56 | 56 | -60.0% | -0.8% | -69.5% | +0.0 (3.1) | n/a | FAIL | $0 |
| 13 | K league:NFL | MOVE_follow | $2,915,441 | 45 | 45 | -24.1% | -7.0% | -38.2% | -0.2 (3.1) | n/a | FAIL | $0 |
| 14 | PM elections | MOVE_follow | $2,900,971 | 60 | 60 | -28.6% | -10.5% | -40.3% | -0.3 (3.1) | n/a | FAIL | $0 |
| 15 | PM politics | FAV_fade | $2,153,074 | 40 | 21 | -60.0% | -42.1% | -103.6% | -0.5 (3.1) | n/a | FAIL | $0 |
| 16 | K league:NCAAF | MOVE_fade | $3,983,507 | 116 | 116 | -29.6% | -15.6% | -48.8% | -0.7 (3.1) | n/a | FAIL | $0 |
| 17 | PM elections | MOVE_fade | $2,900,971 | 59 | 59 | -22.2% | -35.1% | -74.0% | -0.7 (3.1) | n/a | FAIL | $0 |
| 18 | PM politics | FAV_buy | $2,153,074 | 39 | 21 | -0.6% | -4.8% | -20.3% | -0.8 (3.1) | n/a | FAIL | $0 |
| 19 | PM politics | LS_buy | $2,153,074 | 59 | 33 | -103.5% | -71.6% | -104.3% | -0.9 (3.1) | n/a | FAIL | $0 |
| 20 | K league:NCAAMB | LS_buy | $2,146,862 | 61 | 26 | -106.5% | -106.6% | -106.7% | -1.2 (3.1) | n/a | FAIL | $0 |
| 21 | PM elections | FAV_fade | $2,900,971 | 63 | 25 | -103.5% | -84.7% | -103.7% | -1.3 (3.1) | n/a | FAIL | $0 |
| 22 | K league:NHL | MOVE_fade | $1,029,153 | 40 | 40 | -11.1% | -25.6% | -61.9% | -1.4 (3.1) | n/a | FAIL | $0 |
| 23 | K league:NFL | LS_fade | $2,915,441 | 57 | 21 | -6.4% | -6.1% | -19.5% | -1.4 (3.1) | n/a | FAIL | $0 |
| 24 | PM elections | LS_buy | $2,900,971 | 76 | 34 | -102.8% | -103.7% | -103.8% | -1.6 (3.1) | n/a | FAIL | $0 |
| 25 | K league:NHL | MOVE_follow | $1,029,153 | 40 | 40 | -21.6% | -27.0% | -58.8% | -1.8 (3.1) | n/a | FAIL | $0 |
| 26 | K league:NFL | MOVE_fade | $2,915,441 | 45 | 45 | +38.5% | -56.4% | -81.6% | -2.1 (3.1) | n/a | FAIL | $0 |
| 27 | K league:NCAAMB | MOVE_follow | $2,146,862 | 66 | 66 | -18.9% | -36.7% | -65.7% | -2.2 (3.1) | n/a | FAIL | $0 |
| 28 | K league:NCAAMB | FAV_buy | $2,146,862 | 61 | 24 | -12.0% | -11.4% | -42.8% | -2.6 (3.1) | n/a | FAIL | $0 |
| 29 | PM nba | MOVE_follow | $1,314,394 | 43 | 43 | -36.8% | -65.5% | -89.2% | -3.5 (3.1) | n/a | FAIL | $0 |
| 30 | K league:NCAAF | MOVE_follow | $3,983,507 | 116 | 116 | -26.1% | -29.8% | -47.0% | -3.7 (3.1) | n/a | FAIL | $0 |
| 31 | K league:NBA | LS_fade | $10,865,315 | <30 | - | - | - | - | - | - | too few | $0 |
| 32 | K league:NBA | LS_buy | $10,865,315 | <30 | - | - | - | - | - | - | too few | $0 |
| 33 | K league:NBA | FAV_buy | $10,865,315 | <30 | - | - | - | - | - | - | too few | $0 |
| 34 | K league:NBA | FAV_fade | $10,865,315 | <30 | - | - | - | - | - | - | too few | $0 |
| 35 | K league:NCAAF | LS_fade | $3,983,507 | <30 | - | - | - | - | - | - | too few | $0 |
| 36 | K league:NCAAF | LS_buy | $3,983,507 | <30 | - | - | - | - | - | - | too few | $0 |
| 37 | K league:NCAAF | FAV_buy | $3,983,507 | <30 | - | - | - | - | - | - | too few | $0 |
| 38 | K league:NCAAF | FAV_fade | $3,983,507 | <30 | - | - | - | - | - | - | too few | $0 |
| 39 | K league:NFL | FAV_buy | $2,915,441 | <30 | - | - | - | - | - | - | too few | $0 |
| 40 | K league:NFL | FAV_fade | $2,915,441 | <30 | - | - | - | - | - | - | too few | $0 |
| 41 | PM nba | LS_fade | $1,314,394 | <30 | - | - | - | - | - | - | too few | $0 |
| 42 | PM nba | LS_buy | $1,314,394 | <30 | - | - | - | - | - | - | too few | $0 |
| 43 | PM nba | FAV_buy | $1,314,394 | <30 | - | - | - | - | - | - | too few | $0 |
| 44 | PM nba | FAV_fade | $1,314,394 | <30 | - | - | - | - | - | - | too few | $0 |
| 45 | PM fed | LS_fade | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 46 | PM fed | LS_buy | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 47 | PM fed | FAV_buy | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 48 | PM fed | FAV_fade | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 49 | PM fed | MOVE_follow | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 50 | PM fed | MOVE_fade | $1,139,405 | <30 | - | - | - | - | - | - | too few | $0 |
| 51 | K league:NHL | LS_fade | $1,029,153 | <30 | - | - | - | - | - | - | too few | $0 |
| 52 | K league:NHL | LS_buy | $1,029,153 | <30 | - | - | - | - | - | - | too few | $0 |
| 53 | K league:NHL | FAV_buy | $1,029,153 | <30 | - | - | - | - | - | - | too few | $0 |
| 54 | K league:NHL | FAV_fade | $1,029,153 | <30 | - | - | - | - | - | - | too few | $0 |

1 of 54 tests pass. Net returns are per $ staked after fees and slippage, hold to settlement.
Not a claim of edge: the sample is the last 60 days of resolved markets only (venue API limit), a PASS still needs a forward test.

## Replication of the single PASS (PM nba MOVE_fade), fresh random samples of the same unit
- seed 8, slip 1.5c: test -10.0%, lo95 -66.6%, z -0.2 -> FAIL
- seed 9, slip 3.0c: test +46.8%, lo95 -8.1%, z +1.6 (need 2.4) -> FAIL
Verdict: the one PASS did not replicate. Treat as $0/day. Hourly PM price history (last-trade based) can fake mean reversion via bid-ask bounce.
Caveats: Kalshi gate is a single-day (Tue 10-11 Nov) 24h snapshot; PM fed had only 6 usable price paths; NBA/NCAAF/NFL/NHL Kalshi LS/FAV rules had <30 observations (extreme-price checkpoints are rare), i.e. untested, not failed.
