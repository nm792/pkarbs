# Kalshi AAA gas sizing, run gas-sizing-20261119T0231Z (code 91c4e22f0083feb8cd1579366d99fa116e59ed5a)
Sim on real Kalshi data (public API, analysis only). Window: last 60 days to run time. Share = 0.05 x contracts traded in the 2 candles after entry.
Counters: {"markets_listed": 40107, "events_listed": 2224, "events_no_prints": 110, "strikes_near_print": 25000, "entry_out_of_band": 46535, "entry_beyond_life": 9964, "strikes_no_candles": 1018, "entry_dead_excluded": 8882, "events_no_signal": 30, "api_calls": 1344, "api_429": 270, "api_fail": 0, "series_requested": 48}

## Point 1: volume
| family | all-strike contracts listed (life, window) | per day | near-print-strike contracts (life) per day | near-print $ (contracts x candle mid) per day |
|---|---:|---:|---:|---:|
| national | 26,704,261 | 445,071 | 314,168 | 98,351 |
| cached12 | 17,819,248 | 296,987 | 161,155 | 62,321 |
| fresh35 | 24,120,616 | 402,010 | 231,035 | 93,054 |

## Points 3-5: by route, entry, family
R1 = taker (control); R2 = resting bid, UPPER BOUND (queue unknown); maker fee 0 (assumed) and 0.0175 p(1-p) sensitivity (assumed).

| family | entry candle | route | obs (events) | hit vs implied | spread | gap (95% CI) | placebo z | fill rate | $/day (95% CI) | capital/day | worst day | pass |
|---|---|---|---|---|---:|---|---:|---:|---|---:|---:|---|
| national | 1 | R1 taker | 72 (49) | 48.6% vs 49.8% | 2c | -3.97c (-16.86, +10.15) | -0.2 | 100% | $15 ($-37, $69) | $195 | $-467 | FAIL/UNPROVEN |
| national | 1 | R2 bid, maker fee 0 | 63 (46) | 49.2% vs 50.2% | 2c | -0.62c (-13.85, +13.28) | -0.1 | 88% | $30 ($-20, $78) | $174 | $-451 | FAIL/UNPROVEN |
| national | 1 | R2 bid, maker fee 0.0175 | 63 (46) | 49.2% vs 50.2% | 2c | -1.02c (-14.11, +13.04) | -0.2 | 88% | $29 ($-22, $79) | $174 | $-453 | FAIL/UNPROVEN |
| national | 6 | R1 taker | 48 (37) | 56.2% vs 54.0% | 2c | -0.20c (-15.19, +14.48) | +0.3 | 100% | $19 ($-28, $67) | $155 | $-431 | FAIL/UNPROVEN |
| national | 6 | R2 bid, maker fee 0 | 48 (37) | 56.2% vs 54.0% | 2c | +2.60c (-12.53, +16.76) | +0.3 | 100% | $26 ($-21, $78) | $152 | $-409 | FAIL/UNPROVEN |
| national | 6 | R2 bid, maker fee 0.0175 | 48 (37) | 56.2% vs 54.0% | 2c | +2.21c (-12.79, +16.55) | +0.3 | 100% | $25 ($-22, $76) | $152 | $-412 | FAIL/UNPROVEN |
| national | 12 | R1 taker | 27 (26) | 40.7% vs 54.1% | 2c | -15.94c (-32.77, +1.60) | -1.5 | 100% | $-69 ($-152, $-7) | $159 | $-1,905 | FAIL/UNPROVEN |
| national | 12 | R2 bid, maker fee 0 | 27 (26) | 40.7% vs 54.1% | 2c | -13.11c (-31.77, +5.15) | -1.5 | 100% | $-61 ($-145, $4) | $155 | $-1,839 | FAIL/UNPROVEN |
| national | 12 | R2 bid, maker fee 0.0175 | 27 (26) | 40.7% vs 54.1% | 2c | -13.50c (-30.20, +4.47) | -1.5 | 100% | $-62 ($-145, $3) | $155 | $-1,849 | FAIL/UNPROVEN |
| national | all | R1 taker | 147 (50) | 49.7% vs 52.0% | 2c | -4.94c (-16.89, +7.45) | -0.4 | 100% | $-35 ($-173, $93) | $509 | $-2,058 | FAIL/UNPROVEN |
| national | all | R2 bid, maker fee 0 | 138 (49) | 50.0% vs 52.3% | 2c | -1.94c (-14.15, +10.31) | -0.3 | 94% | $-5 ($-147, $135) | $481 | $-1,982 | FAIL/UNPROVEN |
| national | all | R2 bid, maker fee 0.0175 | 138 (49) | 50.0% vs 52.3% | 2c | -2.34c (-15.41, +9.41) | -0.4 | 94% | $-8 ($-145, $121) | $481 | $-1,993 | FAIL/UNPROVEN |
| cached12 | 1 | R1 taker | 1184 (434) | 61.4% vs 51.8% | 49c | -15.74c (-19.81, -11.85) | +4.9 | 100% | $-64 ($-111, $-24) | $176 | $-1,304 | FAIL/UNPROVEN |
| cached12 | 1 | R2 bid, maker fee 0 | 200 (135) | 37.0% vs 50.9% | 49c | -13.66c (-20.85, -6.01) | -3.4 | 17% | $-47 ($-79, $-19) | $67 | $-918 | FAIL/UNPROVEN |
| cached12 | 1 | R2 bid, maker fee 0.0175 | 200 (135) | 37.0% vs 50.9% | 49c | -14.06c (-21.13, -6.38) | -3.2 | 17% | $-47 ($-83, $-20) | $67 | $-925 | FAIL/UNPROVEN |
| cached12 | 6 | R1 taker | 770 (390) | 53.6% vs 50.4% | 39c | -17.64c (-21.64, -13.57) | +1.6 | 100% | $-18 ($-34, $-3) | $70 | $-323 | FAIL/UNPROVEN |
| cached12 | 6 | R2 bid, maker fee 0 | 186 (147) | 32.8% vs 46.6% | 39c | -13.58c (-20.04, -7.35) | -3.7 | 24% | $-7 ($-18, $3) | $30 | $-158 | FAIL/UNPROVEN |
| cached12 | 6 | R2 bid, maker fee 0.0175 | 186 (147) | 32.8% vs 46.6% | 39c | -13.98c (-19.96, -7.50) | -4.0 | 24% | $-7 ($-18, $3) | $30 | $-159 | FAIL/UNPROVEN |
| cached12 | 12 | R1 taker | 420 (276) | 44.0% vs 50.3% | 35c | -25.15c (-29.73, -20.25) | -2.7 | 100% | $-22 ($-39, $-7) | $60 | $-350 | FAIL/UNPROVEN |
| cached12 | 12 | R2 bid, maker fee 0 | 182 (148) | 32.4% vs 48.0% | 35c | -15.40c (-21.96, -8.63) | -4.0 | 43% | $-12 ($-26, $-0) | $35 | $-299 | FAIL/UNPROVEN |
| cached12 | 12 | R2 bid, maker fee 0.0175 | 182 (148) | 32.4% vs 48.0% | 35c | -15.80c (-22.38, -9.31) | -4.1 | 43% | $-12 ($-26, $-1) | $35 | $-301 | FAIL/UNPROVEN |
| cached12 | all | R1 taker | 2374 (491) | 55.8% vs 51.1% | 43c | -18.02c (-21.34, -14.71) | +2.9 | 100% | $-104 ($-158, $-56) | $305 | $-1,328 | FAIL/UNPROVEN |
| cached12 | all | R2 bid, maker fee 0 | 568 (309) | 34.2% vs 48.6% | 43c | -14.19c (-18.50, -9.26) | -5.5 | 24% | $-66 ($-104, $-33) | $131 | $-930 | FAIL/UNPROVEN |
| cached12 | all | R2 bid, maker fee 0.0175 | 568 (309) | 34.2% vs 48.6% | 43c | -14.59c (-19.10, -9.84) | -5.6 | 24% | $-67 ($-104, $-34) | $131 | $-938 | FAIL/UNPROVEN |
| fresh35 | 1 | R1 taker | 1941 (808) | 60.5% vs 50.7% | 41c | -11.60c (-14.85, -8.37) | +6.2 | 100% | $-2 ($-20, $14) | $106 | $-247 | FAIL/UNPROVEN |
| fresh35 | 1 | R2 bid, maker fee 0 | 234 (176) | 41.5% vs 49.6% | 41c | -8.05c (-15.12, -1.12) | -2.2 | 12% | $-9 ($-22, $4) | $37 | $-202 | FAIL/UNPROVEN |
| fresh35 | 1 | R2 bid, maker fee 0.0175 | 234 (176) | 41.5% vs 49.6% | 41c | -8.45c (-15.39, -1.32) | -2.3 | 12% | $-9 ($-23, $4) | $37 | $-203 | FAIL/UNPROVEN |
| fresh35 | 6 | R1 taker | 1362 (739) | 52.9% vs 50.7% | 37c | -17.28c (-20.74, -13.93) | +1.4 | 100% | $-45 ($-90, $-12) | $115 | $-1,112 | FAIL/UNPROVEN |
| fresh35 | 6 | R2 bid, maker fee 0 | 277 (227) | 36.8% vs 48.6% | 37c | -11.53c (-17.78, -4.77) | -3.2 | 20% | $-26 ($-53, $-5) | $59 | $-624 | FAIL/UNPROVEN |
| fresh35 | 6 | R2 bid, maker fee 0.0175 | 277 (227) | 36.8% vs 48.6% | 37c | -11.93c (-18.52, -5.54) | -3.2 | 20% | $-27 ($-56, $-6) | $59 | $-629 | FAIL/UNPROVEN |
| fresh35 | 12 | R1 taker | 741 (493) | 46.7% vs 50.6% | 34c | -22.06c (-26.36, -17.63) | -1.9 | 100% | $-35 ($-65, $-13) | $91 | $-599 | FAIL/UNPROVEN |
| fresh35 | 12 | R2 bid, maker fee 0 | 244 (215) | 29.1% vs 47.3% | 34c | -17.93c (-23.73, -12.30) | -5.4 | 33% | $-28 ($-53, $-11) | $45 | $-633 | FAIL/UNPROVEN |
| fresh35 | 12 | R2 bid, maker fee 0.0175 | 244 (215) | 29.1% vs 47.3% | 34c | -18.33c (-24.09, -12.29) | -5.2 | 33% | $-29 ($-54, $-12) | $45 | $-639 | FAIL/UNPROVEN |
| fresh35 | all | R1 taker | 4044 (957) | 55.4% vs 50.6% | 38c | -15.43c (-18.26, -12.63) | +3.6 | 100% | $-82 ($-140, $-31) | $312 | $-1,135 | FAIL/UNPROVEN |
| fresh35 | all | R2 bid, maker fee 0 | 755 (487) | 35.8% vs 48.5% | 38c | -12.52c (-16.76, -8.61) | -5.5 | 19% | $-63 ($-104, $-30) | $140 | $-681 | FAIL/UNPROVEN |
| fresh35 | all | R2 bid, maker fee 0.0175 | 755 (487) | 35.8% vs 48.5% | 38c | -12.92c (-16.78, -8.74) | -5.6 | 19% | $-65 ($-106, $-30) | $140 | $-687 | FAIL/UNPROVEN |
| ALL | 1 | R1 taker | 3197 (1291) | 60.6% vs 51.1% | 43c | -12.96c (-15.56, -10.58) | +7.7 | 100% | $-51 ($-125, $19) | $477 | $-1,633 | FAIL/UNPROVEN |
| ALL | 1 | R2 bid, maker fee 0 | 497 (357) | 40.6% vs 50.2% | 43c | -9.36c (-14.08, -4.59) | -3.8 | 16% | $-25 ($-86, $36) | $278 | $-1,215 | FAIL/UNPROVEN |
| ALL | 1 | R2 bid, maker fee 0.0175 | 497 (357) | 40.6% vs 50.2% | 43c | -9.77c (-14.47, -4.89) | -3.7 | 16% | $-27 ($-90, $32) | $278 | $-1,225 | FAIL/UNPROVEN |
| ALL | 6 | R1 taker | 2180 (1166) | 53.3% vs 50.6% | 37c | -17.03c (-19.59, -14.53) | +2.1 | 100% | $-44 ($-114, $21) | $339 | $-1,457 | FAIL/UNPROVEN |
| ALL | 6 | R2 bid, maker fee 0 | 511 (411) | 37.2% vs 48.4% | 37c | -10.95c (-15.45, -6.27) | -4.6 | 23% | $-7 ($-64, $46) | $240 | $-947 | FAIL/UNPROVEN |
| ALL | 6 | R2 bid, maker fee 0.0175 | 511 (411) | 37.2% vs 48.4% | 37c | -11.35c (-15.79, -6.82) | -4.6 | 23% | $-9 ($-67, $47) | $240 | $-955 | FAIL/UNPROVEN |
| ALL | 12 | R1 taker | 1188 (795) | 45.6% vs 50.6% | 34c | -23.01c (-26.19, -19.98) | -3.2 | 100% | $-126 ($-215, $-55) | $310 | $-1,889 | FAIL/UNPROVEN |
| ALL | 12 | R2 bid, maker fee 0 | 453 (389) | 31.1% vs 48.0% | 34c | -16.62c (-20.79, -12.19) | -6.8 | 38% | $-101 ($-188, $-34) | $234 | $-1,828 | FAIL/UNPROVEN |
| ALL | 12 | R2 bid, maker fee 0.0175 | 453 (389) | 31.1% vs 48.0% | 34c | -17.03c (-21.32, -12.70) | -6.7 | 38% | $-103 ($-196, $-36) | $234 | $-1,838 | FAIL/UNPROVEN |
| ALL | all | R1 taker | 6565 (1498) | 55.4% vs 50.8% | 39c | -16.13c (-18.20, -14.01) | +4.5 | 100% | $-221 ($-383, $-76) | $1,126 | $-2,303 | FAIL/UNPROVEN |
| ALL | all | R2 bid, maker fee 0 | 1461 (845) | 36.5% vs 48.9% | 39c | -12.17c (-15.32, -9.16) | -7.5 | 22% | $-134 ($-285, $4) | $752 | $-2,067 | FAIL/UNPROVEN |
| ALL | all | R2 bid, maker fee 0.0175 | 1461 (845) | 36.5% vs 48.9% | 39c | -12.57c (-15.71, -9.58) | -7.3 | 22% | $-139 ($-287, $-1) | $752 | $-2,087 | FAIL/UNPROVEN |

Depth at decision time: UNKNOWN (no historical book; see locked rule). Rebates: none modelled. Daily-P&L correlation with other candidates: UNKNOWN until they exist.
