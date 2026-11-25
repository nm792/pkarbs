# SPEC v1 (25 Nov 2026): perp catch-up on the Polymarket SPY "Up or Down" daily, Nautilus-native live paper node. Written by the perps thread (R-086(6), due 12:00Z)

Paper only, no orders ever (SETTLED A6/A7). STATUS: SPEC ONLY. Nothing here is built for Nautilus. The recorder (book_logger_v2, IT task P-PERP-BOOKV2) is the evidence feed, not the paper node. All $ figures are SIM or FLOOR; nothing is MEASURED until the node runs.

## 0. The trade in one paragraph
The Polymarket perp SP500-USD moves first; the SPY Up/Down token books reprice later. When the perp mark moves 10 bp or more in 60 s, buy the token that has not moved yet (Up for an up move, Down for a down move) at its OWN best ask, 5 shares or the touch size, and sell it at its OWN best bid once the book has caught up half the model jump, or after 15 minutes. No hold to resolution. One contract family: one token pair per trading day.

## 1. Known facts (each cited; each must hold or the node does not start)
| # | Fact | Source |
|---|---|---|
| F1 | Each token has its own book; price from its own asks and bids only; NO (Down) never derived from YES (Up) | SETTLED A1 |
| F2 | Historical prints cannot test it. 620 perp moves of >= 10 bp in 60 s (79 events, 3 Aug - 20 Nov); for the 393 with a prior price, the median time until a PRINT covers half the jump is 253 s, 28% not caught up in 30 min. Buying prints the perp calls stale lost: -$20,285 (CI -$68k to +$36k) | reviewer/prototypes/perp-spy-daily/LAG-RESULT-v2.md |
| F3 | Catch-up trade on history: UNDERPOWERED, 38 trades on 27 of 79 events, mean -2.9c per share (CI -6.9c to +1.0c); a planted +3c edge was not detected (CI -3.9c to +4.0c), so no "no edge" call is allowed | CATCHUP-RESULT.md |
| F4 | Live books (24 Nov, 13:22-17:15Z, undecided market): 18 moves of >= 10 bp, quote lag median about 28 s (4 s to 512 s; 7 of 18 under 15 s) against 253 s for prints; 5 trades at the real ask, 13 of 18 moves gave no entry because the ask had already moved. Mean +1.0c per share at the locked fee 0.04, **+0.61c at the market's own fee 0.05** (+2.69, +1.73, -0.27, -0.80, -0.31c): 2 of 5 positive | LIVE-CATCHUP-2026-11-24.md (window 1 + 2) |
| F5 | Parallel run by a second Reviewer session on overlapping windows (14:07-16:04Z): 5 trades, +1.23c at fee 0.04. NOT independent of F4 (same hours, same moves): the two are never added | same file |
| F6 | 23 Nov was unusable: the perp opened 3-4% above Friday's close, the market was decided all day (Up 0.93-0.989), no trade was possible. Part of 24 Nov (from 15:50Z, 0.88-0.93 or 0.07-0.15) was also decided. Decided days and hours are a regime cell, reported, not hidden | LIVE-CATCHUP-2026-11-23.md, 24 Nov |
| F7 | Fee: this market's own feeSchedule is rate 0.05, taker only (finance_prices_fees), not the 0.04 the rule locked from older SPY events. The node reads each market's own rate | gamma, read by the Reviewer 24 Nov ~17:20Z |
| F8 | Touch size at entry: 59.7, 50.0, 80.5 shares (about $20-27 per trade) on the three window-1 trades; one window-2 trade had only 5 shares at the ask. $200 per trade is therefore NOT reachable; the touch is the cap | LIVE-CATCHUP-2026-11-24.md |
| F9 | Scale: about 5 trades a day, 50-80 shares at the touch, +0.6c to +1c per share = about $2-4/day (FLOOR/SIM). Detecting a 1c edge needs a few hundred trades: about 60 trading days at this rate | same file |
| F10 | Recorder cadence: book_logger_v2 polls three endpoints per second and runs at 0.95-0.96 rows/s (15-min checks 13:39Z and 15:36Z, 0 errors). Signal detection can therefore lag a move by up to about 1 s; the 250 ms hold (A3) is applied on top | LIVE-CATCHUP-2026-11-24.md |
| F11 | Planted checks pass: a synthetic 30 s catch-up was measured as 30.2-30.8 s and captured on every move where the book had not already moved (11 of 11, +2.07c per share) | LIVE-CATCHUP-2026-11-24.md (parallel run) |
| F12 | C0 for each day = the perp mark at the prior 21:00Z close, known before the window; it differs from Yahoo ^GSPC's prior close by a median 3.2 bp (p90 9.8 bp, 74 events) | LAG-RESULT-v2.md |

## 2. Rule (frozen; the live section of CATCHUP-RULE.md, 2049e5a5, with the F7 fee correction; no refit)
- Signal: |ln(P_t / P_{t-60 s})| >= 10 bp on the perp 1 s mark; skip 10 minutes after a move. dp = the model's fair jump over the minute (model, TRAIN sigma and mu as in LAG-RULE-v2.md / result.json, frozen).
- Stale token: Up for an up move, Down for a down move. q0 = that token's own mid on the poll before the move.
- Entry: the first own-book update at or after t + 0.25 s (A3 hold) where the token's own best ask <= q0 + |dp|/2 (still stale) and 0.05 < ask < 0.95. IOC limit at the walked ask, size = min(touch size, $200 / ask), never below the 5-share minimum (below it: skip and log). Cap $2,000/day (not binding at F8 sizes).
- Exit: the token's own best bid >= q0 + |dp|/2 (caught up), or the 900 s time stop (the book's own bid at the stop). Never held to resolution.
- P&L per share = exit - entry - fee(entry) - fee(exit), each fee = rate x p x (1-p) with the market's own rate (F7).
- Pre-registered cells (reported separately, never pooled): move size 10-20 bp and > 20 bp; US session vs outside; entry delay <= 10 s, 10-30 s, > 30 s; decided vs undecided regime (ask outside 0.12-0.88 at the move). Variants (5 bp threshold, N or S changes) are OFFLINE on recorded books only, frozen before they are read; the live node runs the 10 bp / 900 s primary only.

## 3. Nautilus node (the only simulator; no custom fill or P&L code)
| Setting | Value |
|---|---|
| node | own TradingNode, trader id PKCATCHUP-001, own paper account, own engine, own process |
| data | Polymarket live data client: order book deltas AND trade ticks for BOTH tokens of the day's market; plus a thin custom Actor that feeds the Polymarket perp SP500-USD 1 s mark and bid/ask (api.perpetuals.polymarket.com; no native Nautilus adapter, UNVERIFIED) as custom data. The Actor only publishes the signal; it places nothing and computes no P&L |
| trade_execution | True |
| queue_position | True |
| liquidity_consumption | True |
| latency | 250 ms (A3) on the live node; 0 / 1,000 ms cells offline on recorded data |
| orders | IOC LIMIT at the walked own ask for entry; marketable-limit exit at the own best bid or at the stop; no execution client |
| daily lifecycle | the slug is spy-up-or-down-on-<month>-<day>-<year>; holidays have no market and the node idles (a missing slug is not an error) |
An unsupported setting on the pinned version, or a missing perp feed, means the node does not start.

## 4. Modelling principles (MODELLING-PRINCIPLES.md)
| s | Requirement | How |
|---|---|---|
| 2 | Power with planted edge | replay recorded books with a planted +3c catch-up on every move; must be detected; a null replay with no move must be silent (F11 passed for the logger; the node must repeat it) |
| 4 | Breadth | the independent unit is the TRADING DAY (moves within a day share one regime); trades are not the sample size |
| 5 | Shrinkage | rank cells on shrunk mean per share; report the raw count beside it |
| 8 | No hindsight | C0, sigma, mu and thresholds frozen in a committed config before day 1; decisions use only data received before the decision time |
| 10 | Fills not random | entry is IOC at the own ask, so fill risk is the 250 ms hold; record the ask at t+0.25 s vs the ask at the first poll to measure the hold's cost per move |
| 11 | Regime | decided vs undecided, session vs outside, per month; report the share of days that are unusable (F6) |
| 12 | Noise | per-trade P&L after fees is primary, 60 s markout secondary; settlement is not a P&L source (no hold to resolution) |
| 13 | Sequential stops | 10 blind trading days, then an always-valid 95% interval on the mean per share per cell; success lower > 0 with >= 30 trades, futility upper < 0, 60 days maximum |
| 14 | Capacity | $/day only from measured own-ask depth at each decision (F8 says $20-27 per trade); node logs touch size for every signal, including skipped ones; FLOOR label until then |

## 5. Start gates (none true today)
G1 Prime recorder: IT's R-058 pre-flight for P-PERP-BOOKV2 pasted and passing (no paste seen at 06:00Z 25 Nov). G2 IT confirms the Nautilus version and each setting in section 3. G3 the perp-feed Actor and the config are built with can-fail tests (offline code: the perps thread does this without asking, R-047). G4 the planted-edge and null replays pass on recorded books (live_2026-11-24_*_book_v2 files). G5 frozen config committed before the first day. G6 ONE NEEDS-NICK INBOX row for the server step (deploying a paper node on Prime is server code); the default if Nick does not answer: the node stays unbuilt, the recorder keeps collecting, offline replays continue.

## 6. Stand-alone vs bar
NOT shown to clear $200/day. F9: about $2-4/day on 5 trades a day at touch size, sign uncertain (2 of 5 trades positive at the true fee). Stack layer: yes, a small one, and it shares the perp feed with the weekend perps legs. What settles it: about 60 trading days of the node's own paper fills through the stops, or a different cell (a wider move set, a different instrument with deeper books) frozen in advance; nothing changes before that.

Confidence 6/10 as a spec: F2-F11 are quoted from the Reviewer's files and not re-run by me; the Nautilus class names for the Polymarket data client and the custom perp feed are UNVERIFIED on the pinned version. To reach 9: IT confirms the settings, the gate signs the table, and the planted replay runs on the node.
