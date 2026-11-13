# Kalshi gas: buy the early favourite (favoured side at the ask, hold to settlement)
Whole available history (live + /historical). TEST = second half by close date. gap = win rate - ask - Kalshi fee (0.07 p(1-p)). size = 10% of the $ traded on that market in the 2 hours from the checkpoint (x0.5 taker-buy share). $/day = sum(size x net return)/days, event-clustered 95% CI.

| series | checkpoint | half | markets (events) | favourite ask | win rate | gap net of fee (95% CI) | net/$ | size per market | $/day (lo95) | days |
|---|---|---|---|---:|---:|---|---:|---:|---|---:|
<!-- national daily: 4119 resolved markets listed, 250 sampled, history 2026-09-06 to 2026-11-07 -->
| national daily | first hour | train | 22 (18) | 88.7c | 90.9% | +1.66c (-11.37, +11.81) | +2.73% | $84 | $9 ($-101) | 29 |
| national daily | first hour | TEST | 20 (16) | 92.2c | 100.0% | +7.31c (+3.92, +11.64) | +9.27% | $196 | $181 ($82) | 33 |
| national daily | 10% of life | train | 22 (18) | 88.7c | 90.9% | +1.66c (-12.92, +12.07) | +2.73% | $84 | $9 ($-95) | 29 |
| national daily | 10% of life | TEST | 20 (16) | 92.2c | 100.0% | +7.31c (+3.79, +12.03) | +9.27% | $196 | $181 ($89) | 33 |
| national daily | 25% of life | train | <20 obs | | | | | | | |
| national daily | 25% of life | TEST | <20 obs | | | | | | | |
<!-- state daily: 45467 resolved markets listed, 250 sampled, history 2026-09-09 to 2026-11-10 -->
| state daily | first hour | train | 85 (84) | 93.3c | 87.1% | -6.62c (-13.40, -0.15) | -6.77% | $6 | $46 ($22) | 36 |
| state daily | first hour | TEST | 80 (76) | 94.6c | 93.8% | -1.11c (-6.08, +3.49) | -1.28% | $2 | $-9 ($-142) | 26 |
| state daily | 10% of life | train | 85 (84) | 93.3c | 87.1% | -6.62c (-14.36, -0.36) | -6.77% | $6 | $46 ($21) | 36 |
| state daily | 10% of life | TEST | 80 (76) | 94.6c | 93.8% | -1.11c (-6.28, +3.03) | -1.28% | $2 | $-9 ($-153) | 26 |
| state daily | 25% of life | train | 81 (80) | 93.0c | 85.2% | -8.19c (-15.84, -0.74) | -8.80% | $7 | $-209 ($-767) | 36 |
| state daily | 25% of life | TEST | 81 (78) | 95.3c | 95.1% | -0.57c (-5.70, +3.88) | -0.08% | $14 | $126 ($24) | 26 |
<!-- national weekly: 1127 resolved markets listed, 250 sampled, history 2026-09-07 to 2026-11-09 -->
| national weekly | first hour | train | 29 (5) | 88.0c | 89.7% | +1.01c (-11.38, +10.45) | +4.16% | $27 | $11 ($4) | 28 |
| national weekly | first hour | TEST | 26 (5) | 88.2c | 80.8% | -7.97c (-13.30, -2.62) | -11.42% | $114 | $-49 ($-187) | 35 |
| national weekly | 10% of life | train | 25 (5) | 86.0c | 80.0% | -6.74c (-24.60, +5.81) | -7.63% | $18 | $1 ($-2) | 28 |
| national weekly | 10% of life | TEST | 23 (5) | 88.9c | 82.6% | -6.84c (-10.09, -2.34) | -10.82% | $97 | $-23 ($-54) | 35 |
| national weekly | 25% of life | train | 27 (5) | 86.6c | 74.1% | -13.23c (-34.88, -0.87) | -21.17% | $7 | $-1 ($-5) | 28 |
| national weekly | 25% of life | TEST | 23 (5) | 91.2c | 87.0% | -4.65c (-17.79, +8.49) | -5.52% | $52 | $15 ($-32) | 35 |
<!-- national monthly: 493 resolved markets listed, 250 sampled, history 2026-09-30 to 2026-10-31 -->
| national monthly | first hour | train | 28 (2) | 86.5c | 75.0% | -12.13c (-12.82, -11.61) | -17.57% | $8 | $-2 ($-2) | 31 |
| national monthly | first hour | TEST | <20 obs | | | | | | | |
| national monthly | 10% of life | train | 28 (2) | 88.6c | 82.1% | -7.00c (-21.28, +5.37) | -9.69% | $1 | $-1 ($-2) | 31 |
| national monthly | 10% of life | TEST | <20 obs | | | | | | | |
| national monthly | 25% of life | train | 28 (2) | 89.1c | 82.1% | -7.57c (-21.54, +4.54) | -9.65% | $1 | $-1 ($-1) | 31 |
| national monthly | 25% of life | TEST | <20 obs | | | | | | | |

$/day is scaled from the sample to all listed resolved markets. Held to settlement; no exits modelled.
