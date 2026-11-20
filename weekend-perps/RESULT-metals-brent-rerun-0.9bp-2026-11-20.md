# RESULT: Sunday-reopen metals fade / Brent follow, RERUN at the sourced cost table (20 Nov 2026)

**Goal:** reach $200-500/day automated by stacking small positive-EV layers (gas is one). **Where this stands:** this layer has NO reliable number yet; it is an unproven, tiny stack candidate (verdict section).
Rule: unchanged `weekend-perps/LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md` (branch claude/project-thread-ogfnfn, head 05ecdb99e3). Only change: fee 9 bp -> 0.9 bp per side per `LOCKED-RULE-cost-table-2026-11-17.md` and Reviewer REVIEW-2026-11-17-false-negatives item 1 (agreed 17 Nov). No tuning, no new data (cells = `followups-2026-11-16/oos_cells.json`, fetched 16 Nov; same signals, same 50 bp threshold, same exit, same seed-1 weekend-cluster bootstrap).
Code: `rerun_metals.py` (trade/boot/rep logic copied verbatim from `followups-2026-11-16/oos.py`; reads cells instead of refetching). Outputs: `out/rerun_fee0.9.txt`, `out/repro_fee9_4.5.txt`, `out/sizing.txt`.

## Cost table (every term)
| term | value | source | status |
|---|---|---|---|
| xyz SILVER/COPPER/PLATINUM/BRENTOIL taker fee | 0.9 bp/side | growthMode "enabled" for all four in `followups-2026-11-17/rerun-2026-11-17/growth.json`; 4.5 x 2 x 0.1 per cost-table rule; Webb perps-paper.md:58 (second-hand); press reports growth mode cuts HIP-3 taker fees >90% and trade.xyz enabled it for XYZ assets (thedefiant.io, kucoin.com news, Nov 2025; official docs page not retrieved) | SOURCED, docs not read directly |
| half-spread | 1.0 silver/Brent, 4.9 copper, 6.2 platinum bp, unchanged from the rule | l2Book 16 Nov, stress assumption in rule | measured once, multiplier assumed |
| funding | ignored (hold ~1.5 h) | rule | assumption |
| round trip | 2 x (0.9 + half-spread) | | |

## Checks that this rerun can fail
- Reproduction (mutant): fee 9 and 4.5 run through the same code reproduce the 16 Nov published numbers exactly (held-out metals +2.4, CI -83.6 to +103.6; copper +71.0 (-8.4, +166.9); Brent +25.7 (-268.8, +397.2); disc 1 h metals +16.9 (-9.8, +45.7)). `out/repro_fee9_4.5.txt`.
- Constant shift: 9 -> 0.9 moves every net by +16.2 bp; observed (held metals 2.4 -> 18.6). Matches Reviewer arithmetic.
- Rule-to-code table: authored by me, UNCHECKED by another thread (below). Per Reviewer process this is not yet a "pass" and nothing here is a pass.

## Results at 0.9 bp (net bp, weekend-cluster bootstrap 95% CI)
| sample | group | n | weekends | gross | net | CI | weekends right sign |
|---|---|---|---|---|---|---|---|
| discovery 1 h | metals | 35 | 23 | +42.8 | +33.1 | +6.4 to +61.9 | 78% |
| discovery 4 h (coarse) | metals | 36 | 20 | +76.1 | +66.7 | +42.1 to +92.1 | 85% |
| **HELD-OUT 4 h (the locked test)** | **metals** | **25** | **14** | **+27.3** | **+18.6** | **-67.4 to +119.8** | **43%** |
| held-out | silver | 11 | 11 | -25.4 | -29.2 | -143.1 to +136.3 | 27% |
| held-out | copper | 9 | 9 | +98.8 | +87.2 | +7.8 to +183.1 | 78% |
| held-out | platinum | 5 | 5 | +14.7 | +0.5 | -118.7 to +158.0 | 40% |
| discovery 1 h | Brent follow | 22 | 22 | +7.1 | +3.3 | -33.3 to +39.4 | 50% |
| discovery 4 h | Brent follow | 24 | 24 | -17.1 | -20.9 | -71.1 to +28.2 | 42% |
| **HELD-OUT** | **Brent follow** | **7** | **7** | **+45.7** | **+41.9** | **-252.6 to +413.4** | 57% |
(max-weekend-share column is degenerate when total net is near 0; ignore for platinum/Brent.)

## Verdict against the pre-registered rule
- **H-metals: NOT PASSED, unknown.** Held-out CI includes 0, only 43% of weekends have the right sign (rule needs >= 2/3), silver goes the wrong way. Same outcome as at 9 bp; the cost error did not change the locked verdict.
- **H-brent: unknown** (held-out n = 7 < 8). On discovery the Brent trade as defined earns +3 bp (1 h) / -21 bp (4 h), CIs include 0: no tradable edge shown. The "+48 bp (CI +5 to +95, 22 signals)" quoted in the stack audit is a gap measure to the reopen price from `RESULT-pm-drift-and-commodity-fx-2026-11-16.md`; the OOS result file states it was not a tradable profit. It does not become one with the cost fix.
- **Copper held-out +87 bp (CI +8 to +183, n 9)** is a post-hoc sub-cell of a failed locked test; not a pass, flagged as the one cell worth a forward look.
- **Fragility warning (unchanged):** same 30 discovery weekends give +33 bp on 1 h and +67 bp on 4 h candles; held-out uses 4 h only (Hyperliquid candle history cap ~5000 bars is the likely reason 1 h is unavailable before 22 Apr; unverified). Effect size depends on candle resolution, so a real-time test is needed.

## Stand-alone $/day and stack-layer verdict
Estimate only (not measured P&L): signals/week (silver 0.4, copper 0.4, platinum 0.3, Brent 0.7) and book capacity within 5 bp (silver ~$1.0M, copper ~$18k, platinum ~$20k, Brent ~$340k per side) from `RESULT-metals-brent-oos-2026-11-16.md` capacity section (one l2Book snapshot, 16 Nov); net bp from the table above; /7 for calendar days (`out/sizing.txt`).
| per-trade size | discovery nets | held-out nets |
|---|---|---|
| flat $20k (copper/platinum capped at book) | +$10.6/day | +$14.1/day |
| $100k, capped at book | +$25.2/day | +$34.2/day |
| full book capacity (5 bp impact) | +$168/day (silver +$150 carries it) | -$15/day (silver -$167, Brent +$142) |
Reading: **stand-alone about +$10 to +$35/day at realistic size if the point estimates are real; the reliable (CI lower bound) figure is not above $0 on any locked sample**, and the only large figures need silver at ~$1M, where the held-out sign is wrong. **Stack layer: POSSIBLE, UNPROVEN: park as a candidate (Nick's rule), do not build.** It is automatable (one signal per weekend at ~23:00Z Sunday, one exit 60 min later) and has no obvious overlap with gas, but correlation with other layers, shared capital and worst-day loss are unmeasured (SETTLED A9). Venue access from the HK/Japan location is not assessed here.

## What would settle it
1. Forward test: reopen Sun 22 Nov ~23:00Z (CME reopen 18:00 ET) onward, on the weekend-perps logger with metals/Brent books. The task file (agent/TASK-weekend-perps-metals-logger-2026-11-16.md) says "Sun 23 Nov"; 23 Nov 2026 is a Monday, so the date there is wrong. Logger status is UNVERIFIED by me (deadline Thu 20 Nov 12:00Z; needs a live server read before Sunday, per the 30-minute rule).
2. Sample size: discovery net +33 bp with per-trade SD ~68 bp (estimated from the CI) needs about 20 metal signals for a CI lower bound > 0. At 1.1 metal signals/week that is ~18 weekends (~4 months). Copper alone (0.4/wk) is slower. No faster history exists if the 5000-candle cap is the cause.
3. Cheap check: a 1x half-spread sensitivity row and a recorded-book VWAP entry at the logged weekends.

## Rule-to-code table (author-written; NOT YET SIGNED by another thread -> result stays UNCHECKED)
| rule text | code (`rerun_metals.py`) | note |
|---|---|---|
| signal if abs(Sown) >= 50 bp | `abs(c["S"])<50: continue` | cells carry S built by oos.py cells() |
| fade metals = -sign(S), follow Brent = +sign(S) | SYMS pos -1/+1, `pos*sg(S)` | match |
| gross = pos x (exit/entry - 1) in bp | same expression | match |
| net = gross - 2 x (fee + half-spread) | `cost=2*(fee+max(hs,1.0))` | hs as published (1.0/4.9/6.2); fee 0.9 per amendment |
| weekend-cluster bootstrap, 10,000, seed 1 | `boot`, `random.Random(1)` | seed state is per process; repro run reproduces originals exactly |
| held-out = T before 22 Apr, 4 h candles | cells keyed "held" in oos_cells.json | cells not rebuilt; trusted from the 16 Nov run |
| decision rule | applied by hand above | n, CI, 2/3 weekends, 40% share |
Not checked: cell construction (oos.py cells()), Yahoo reference gaps. Request: another thread signs this table and runs a planted-edge series through `trades/boot` before this is relayed as anything but "unknown".

**Confidence 7/10** (correct, mutually exclusive, exhaustive). Held down by: no independent rule-to-code sign-off; fee is second-hand (growth.json + Webb + press, official docs unread); data frozen at 16 Nov and cells not rebuilt; sizing uses one book snapshot and the 16 Nov signal rates; logger status unverified. To reach 9: checker sign-off, official HIP-3 fee page or fills check, live read of the logger before 22 Nov.
