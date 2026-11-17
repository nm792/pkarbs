# RESULT: rerun of the funding-window and follow-up tests after the code was fixed to the locked rules (17 Nov 2026, ~05:45Z)

Rules: LOCKED-RULE-funding-window-divergence-2026-11-17.md, LOCKED-RULE-divergence-followups-2026-11-17.md, amended by LOCKED-RULE-cost-table-2026-11-17.md. Code signed off by an independent checker thread (RULE-TO-CODE-TABLE.md, PR #377/#379, planted-edge and no-edge check passes). This SUPERSEDES RESULT-funding-window-divergence-2026-11-17.md and the Test 2 and 3 results of the first run (those were UNCHECKED). Raw output: followups-2026-11-17/rerun-2026-11-17/. Data fetched 17 Nov ~05:15Z (candles carry open and close). Fees: Polymarket 4 bp; xyz growth-mode 0.9 bp (sourced, see cost table); non-growth xyz and flx/km COST UNCHECKED. Every verdict below is on the sourced-cost subset only.

## Scope change that matters: flx and km are OUT
39 flx and km perps have OI = 0 and an empty live order book now (many are delisted, e.g. flx:TSLA isDelisted true), so no live half-spread exists. Under the rule a symbol without a measured half-spread is excluded, never defaulted. So the funding-window metrics (universe needs OI > 0) cover 108 xyz perps, and Tests 2 and 3 trade only xyz. The earlier flx+km carry result (-45 bp) is void. The BIRD-style frozen-oracle cases on Felix and Kinetiq can NOT be costed from the current books. Test 3 episodes still include 181 flx and 6 km episodes for the descriptive parts only.

## Funding-window metrics (xyz, 108 perps, ~31 weeks)
- Divergence is common: share of hours with |premium| >= 25 bp is 17% thin weekend, 11-18% thin weekday, 3-9% mid, 6% liquid. Hours not reverted by the next settlement: 55-80% (thin weekend 80%). AR(1) 0.5-0.8.
- Reversion trade (|premium| >= 50 bp at the end of an hour, fade, exit at the close of the next hour, funding received counted), sourced-cost net: thin weekend -59.5 (CI -70 to -51, n 1919), thin weekday-US -46, thin weekday-other -61; mid weekend -11.6 (CI -23 to -2), mid weekday-US -40.7, mid weekday-other -14.7; liquid weekend +8.8 (CI -9.4 to +25.3, n 411), liquid weekday-US +0.5 (CI -10.5 to +10.0, n 1087), liquid weekday-other -1.9 (CI -10.9 to +7.8, n 1784). Same trades at the old 9 bp per side are all negative (liquid -6.8 to -18.2).
- Verdict: NO TRADABLE REVERSION in any cell (no cell has CI lower bound above 0). The liquid cells are indistinguishable from zero, not negative: the 9 bp error made them look worse than they are.

## Test 2: hold the faded side 6 hours (primary), sourced cost
All -27.0 (CI -42 to -12, n 4678); thin -43.4 (CI -57 to -29, n 2540); mid -13.7 (CI -44 to +18); liquid -3.5 (CI -34 to +26, n 1273); persistent (3 hours >= 100 bp, hours h, h-1, h-2) -35.4 (CI -82 to +10, n 114, the BIRD-style cell). Verdict: NO TRADABLE CARRY. Sensitivity only (no verdict): k=12 liquid +10.4 (CI -27 to +49), persistent +33 (n 47, CI -70 to +137). Funding received is real (about +8 bp over 6 h, +33 bp in the persistent cell) but the price move against the position and the costs eat it.

## Test 3: frozen-oracle episodes (>= 3 hours with |premium| >= 100 bp)
536 episodes; 84 (16%) reset in the very next hour. Hazard of reset in the next hour 1.4% to 7.5% by run length, no clear rise. Candle return toward the oracle in the reset hour: mean +16 bp, median 0, slope 0.26 on the premium just before the reset (corr 0.09), so the perp does not snap to the oracle on average. Ex-post bound (not tradable): sourced-cost net -0.4 bp (CI -57 to +48, n 267; funding received averages +41 bp but is cancelled by spread cost and price moves). Verdict: NO TRADABLE JUMP. Out-of-sample AUC 0.78 on 20 held-out resets (weekend indicator only; small sample). What the venue settles or liquidates against at unfreeze is NOT verified from docs (hosts blocked).

## Metric 5 (live 30 min sample, 01:02-01:32Z, descriptive only)
23 symbol-windows, 7 with an exceedance >= 25 bp; 4 of 7 (57%) revert below 5 bp within the 30 minutes.

## Test 1 (5 s logger, Polymarket gaps at real book prices): NOT RUN, no valid data yet
My container copy died; the server logger (running since 04:11Z) has to be evaluated by IT (task agent/TASK-logger-boot-persistence-2026-11-17.md step 4, cutoff for funding rates 04:00Z on 18 Nov because the venue keeps only 24 hourly rates). Earlier "5 events" result is void (pre-merge, no funding, whole-series placebo).

## Caveats
Bootstrap CI covers about 88% at 12 clusters (checker's simulation); with 27-31 weekly clusters it is closer to nominal. The 3x spread multiplier is an assumption, as written in the rule. Weekday/weekend classes are applied to commodity and FX perps as a simplification. Hourly history cannot show intra-hour paths.

Confidence: 8/10 that these numbers follow the locked rules (checker signed, planted-edge passes). Not 9 because the 0.9 bp fee rests on the growth-mode flag plus the checker's fill check, flx/km costs are unknown, and Test 1 has no data. To reach 9: IT's Test 1 evaluation, and fills or fee metadata for non-growth and flx/km assets.
