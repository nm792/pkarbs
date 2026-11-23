# R-036 item 1: deep-volume contracts whose prices resolve late (redo of the 11 Nov scan), 22 Nov 2026

Paper only. Code: `pipeline/late_pull.py`, `pipeline/late_leader.py`, `pipeline/forward/resolving_books.py` (48 tests pass). Data: `pipeline/out/listing1/late_leader_table.csv` (81 families), `resolving_books_snap_2026-11-22.json` (157 open events), `late_leader_gamma_check.csv`. Tapes: data-api /v2/trades, 8,729 markets (none truncated), newest resolution 19 Nov 03:45Z, last 40 resolved events per family (15m and hourly families: 1-2 days only).

## Answer (confidence 6/10)
**No family shows a late-price discount that a plain causal rule can take.** Buying the own-token leader at T-1h and holding to resolution earns **$53/day summed over all 81 families, about 26% of $200, and it is a FLOOR** (fills limited to printed BUY $ in the next 10 min, 220 bets in 2,775 events). The same rule at T-3h sums to **-$167/day** and at T-30m to **-$14/day**, so the sign is not stable. Only 5 families have a 95% lower bound above 0 (wti-up-or-down-15m, nvda, tsla, whitehouse, rklb daily); with 81 families chance alone gives about 2, and four of them are under $3/day. The hindsight CEILING (winner bought at 0.70-0.95 in the last 3 h, $200 per event, $2,000/day cap) sums to **$868/day**, but 74% of it ($644) is the four 15-minute commodity series, whose samples are only 1-2 days of tapes. **MEASURED decision-time ask depth does not exist for any family**: no book was ever recorded at T-3h/T-1h. The depth column below is a live snapshot 18-227 hours before the end, not decision time, so it cannot be used for sizing. The recorder that fixes this is an IT row (below).

## Ranked table (top 30 by CEILING; full 81 rows in `late_leader_table.csv`)
Label for every number in the last two columns: **CEILING = hindsight (winner known), FLOOR = causal but print-sized. No cell is MEASURED.** Daily $ volume = sum(price x size) over all trades of all markets of the sampled events divided by the calendar span (NOT gamma volumeNum, which is shares; gamma event volume is 1.4-2.9x these figures in `late_leader_gamma_check.csv`, as expected for shares at an average price of 0.35-0.7). $/day is after a conservative fee of 0.05 x p x (1-p) per share. % of $200 means $/day divided by $200.

| # | contract family | daily $ volume (all tokens) | resolutions/day | own-token ask depth at leader ask..+2c (SNAPSHOT, not decision time) | CEILING $/day [% of $200] (hindsight: winner buys 0.70-0.95, last 3 h) | CAUSAL FLOOR $/day [% of $200] (leader bought at T-1h, prints only; 95% lo; bets/events) |
|---|---|---|---|---|---|---|
| 1 | gold-up-or-down-15m | 11,688 | 40.00 | $3 at ask 0.54 (27 ev, 18-24 h to end) | 506.65 [253.32%] | 1.70 [0.85%] (T-5m; lo -96.88; 25/40) |
| 2 | silver-up-or-down-15m | 2,154 | 40.00 | $3 at ask 0.54 (27 ev, 18-24 h to end) | 84.17 [42.09%] | 22.81 [11.40%] (T-5m; lo -84.92; 14/40) |
| 3 | wti-up-or-down-15m | 1,048 | 15.72 | $308 at ask 0.98 (27 ev, 18-24 h to end) | 41.98 [20.99%] | 29.05 [14.53%] (T-5m; lo 5.52; 11/38) |
| 4 | elon-tweets | 270,996 | 0.29 | $1,082 at ask 0.16 (3 ev, 59-227 h to end) | 21.20 [10.60%] | -2.79 [-1.39%] (T-1h; lo -20.02; 9/9) |
| 5 | elon-tweets-48h | 136,981 | 0.44 | $478 at ask 0.42 (2 ev, 35-83 h to end) | 18.58 [9.29%] | 3.17 [1.58%] (T-1h; lo -5.26; 19/40) |
| 6 | spx-daily-up-or-down | 17,877 | 0.71 | $519 at ask 0.74 (1 ev, 39-39 h to end) | 17.35 [8.68%] | 0.94 [0.47%] (T-1h; lo -9.91; 14/40) |
| 7 | silver-up-or-down-1h | 1,082 | 21.77 | $3 at ask 0.54 (6 ev, 19-24 h to end) | 15.67 [7.83%] | -4.32 [-2.16%] (T-15m; lo -28.44; 7/40) |
| 8 | spy-daily-up-or-down | 6,761 | 0.71 | $45 at ask 0.77 (1 ev, 39-39 h to end) | 15.09 [7.55%] | 2.10 [1.05%] (T-1h; lo -5.46; 10/40) |
| 9 | natgas-up-or-down-15m | 178 | 15.72 | - | 11.58 [5.79%] | -2.48 [-1.24%] (T-5m; lo -11.52; 5/38) |
| 10 | spy-daily-close-uo | 12,901 | 0.71 | $661 at ask 0.91 (1 ev, 39-39 h to end) | 11.45 [5.73%] | 0.00 [0.00%] (T-1h; lo 0.00; 0/40) |
| 11 | wti-daily-close-uo | 13,426 | 0.71 | - | 9.33 [4.67%] | 0.02 [0.01%] (T-1h; lo 0.00; 1/40) |
| 12 | gold-up-or-down-1h | 1,140 | 21.77 | $3 at ask 0.54 (6 ev, 19-24 h to end) | 6.67 [3.33%] | 5.08 [2.54%] (T-15m; lo -10.52; 9/40) |
| 13 | nvda-daily-up-down | 1,292 | 0.71 | $113 at ask 0.94 (1 ev, 39-39 h to end) | 6.53 [3.27%] | 0.14 [0.07%] (T-1h; lo 0.01; 4/40) |
| 14 | msft-multi-strikes-weekly | 2,416 | 0.72 | $41 at ask 0.90 (2 ev, -1906-39 h to end) | 6.14 [3.07%] | 0.00 [0.00%] (T-1h; lo 0.00; 0/22) |
| 15 | trump-truth-social | 11,227 | 0.28 | $364 at ask 0.38 (3 ev, 59-227 h to end) | 5.96 [2.98%] | -0.59 [-0.29%] (T-1h; lo -2.28; 12/40) |
| 16 | msft-daily-up-down | 870 | 0.71 | - | 5.50 [2.75%] | 0.09 [0.05%] (T-1h; lo -0.04; 3/40) |
| 17 | meta-daily-up-down | 1,050 | 0.71 | $115 at ask 0.88 (1 ev, 39-39 h to end) | 5.22 [2.61%] | -1.12 [-0.56%] (T-1h; lo -3.34; 3/40) |
| 18 | amzn-daily-up-down | 635 | 0.71 | - | 4.88 [2.44%] | -1.34 [-0.67%] (T-1h; lo -4.19; 2/40) |
| 19 | oil-daily-up-or-down | 2,716 | 0.71 | - | 4.67 [2.33%] | 0.59 [0.30%] (T-1h; lo 0.00; 1/40) |
| 20 | gold-daily-up-or-down | 2,102 | 0.71 | $22 at ask 0.75 (1 ev, 40-40 h to end) | 4.61 [2.31%] | 0.02 [0.01%] (T-1h; lo 0.00; 1/40) |
| 21 | nvda-multi-strikes-weekly | 2,926 | 0.72 | $85 at ask 0.67 (1 ev, 39-39 h to end) | 4.24 [2.12%] | 0.10 [0.05%] (T-1h; lo 0.00; 1/22) |
| 22 | aapl-daily-up-down | 708 | 0.71 | - | 4.08 [2.04%] | -0.66 [-0.33%] (T-1h; lo -1.94; 2/40) |
| 23 | aapl-multi-strikes-weekly | 957 | 0.72 | - | 3.98 [1.99%] | -0.14 [-0.07%] (T-1h; lo -0.41; 1/22) |
| 24 | googl-daily-up-down | 727 | 0.71 | - | 3.53 [1.76%] | -0.28 [-0.14%] (T-1h; lo -0.99; 3/40) |
| 25 | dow-jones-daily-up-or-down | 694 | 0.71 | - | 3.43 [1.71%] | -1.59 [-0.79%] (T-1h; lo -4.60; 2/40) |
| 26 | tsla-daily-up-down | 997 | 0.71 | - | 3.40 [1.70%] | 2.09 [1.05%] (T-1h; lo 0.02; 4/40) |
| 27 | nflx-daily-up-or-down | 790 | 0.71 | - | 3.28 [1.64%] | -0.20 [-0.10%] (T-1h; lo -0.56; 5/40) |
| 28 | mrbeast-views-day-1 | 8,187 | 0.41 | - | 3.17 [1.58%] | 0.00 [0.00%] (T-1h; lo 0.00; 0/13) |
| 29 | meta-multi-strikes-daily | 2,034 | 0.71 | $538 at ask 0.88 (1 ev, 39-39 h to end) | 3.04 [1.52%] | -0.76 [-0.38%] (T-1h; lo -1.98; 2/40) |
| 30 | whitehouse-daily-tweets | 5,363 | 0.28 | $81 at ask 0.76 (1 ev, 59-59 h to end) | 2.99 [1.50%] | 0.29 [0.14%] (T-1h; lo 0.02; 4/40) |

## Rule and definitions (fixed before the run)
* Contract family = gamma series slug; sample = last 40 resolved events (11 Nov bar kept: daily or more frequent, no sports/esports/crypto/weather/5-minute series; election families are one-offs, see below).
* Decision time t = endDate minus lead. Leads: 3 h / 1 h / 30 min (primary 1 h); for `-15m` series 10 / 5 / 2 min (primary 5 min); for `-1h` series 30 / 15 / 5 min (primary 15 min). The primary was fixed before the run; the other leads are reported in the CSV.
* Leader = candidate token with the highest own last print (<= 12 h old). Candidates = YES token of bracket events, both tokens of single Up/Down markets. Never 1 minus the other token.
* Fill = earliest BUY print of the leader token in [t, t+10 min] (not after the end); size = min($200, printed BUY $ in that window at <= fill + 2c). Hold to resolution. Daily cap $2,000 of fills per ET day. Event-clustered bootstrap (2,000 draws) for the 95% lower bound of $/day.
* CEILING = the winner token's BUY prints priced 0.70-0.95 in the last 3 h (15m: last 15 min; 1h: last hour), cheapest first up to $200 per event, same fee and cap. It uses the winner, so it is not tradable; it shows where the late discount sits.

## What the table does and does not show
* Where the late move is: the weekly Elon and Trump post-count families still hold the largest volume ($271k and $11k a day) and the winner is at 0.46 at T-3h and 0.76 at T-1h (`tweet-endgame-2026-11-20.csv`), but the leader bought at T-1h costs 0.79 and wins 78% (Elon weekly, 9 events), so there is no edge from the leader alone (the Elon nowcast test is in LISTING-STUDY.md; its edge flipped sign between halves).
* Daily Up/Down and strike series: in the two deepest, the leader at T-1h costs about 0.80 and wins 86% (spx) and 80% (spy), a gap of 6 and 2 points; the lower bound is negative on both (-$9.91 and -$5.46 a day). They are uncertain until late, but the leader is not a discount.
* 15-minute series: gold and silver 15m show 40 events/day but only 1 day of tapes; the wti 15m lower bound is +$5.5/day on 38 events and is **UNPROVEN** (2.4 days, one of five chance-level positives).
* Election one-offs (excluded from the ranking, no recurrence after 3 Nov 2026): House/Senate/party-control/Brazil run-off families show $60k to $24.6M of winner $ per window-day (inflated by the one-off event count) (`series-listing-hours-2026-11-20.csv` rows tpl:*), the winner at +1h was 0.75-0.88, i.e. already priced.

## Decision-time depth: what it takes (IT row)
No book was ever stored at decision time for these families, so no MEASURED figure is possible from history. Row: `it/IT-2026-11-22-resolving-books-recorder.md` (service `it/units/resolving-books.service`, series list `it/resolving_books_series.txt`, 34 series, dated windows `it/SCHEDULE-resolving-books-2026-11-22.md`, preflight `it/resolving_books_preflight.sh`, live read `it/resolving_books_live_read.sh`). It snapshots all candidate tokens at T-3h, T-1h and T-30m of each open event, own-token asks and bids. First windows that can still be caught: box-office-openings Sun 22 Nov 09:00Z and 11:00Z (13 open events). NOT RUNNING, UNVERIFIED until IT posts the pid and a growing file. Daily families give about 5 events a week, so 20 events per family takes about 4 weeks; the weekly Elon series (2 a week) takes about 10.

## Corrections to the 11 Nov scan (OUT-step1-late-winner-series-2026-11-11.md)
* It multiplied gamma volume by 0.5 on the belief that gamma counts ~2x trade notional; gamma volumeNum is SHARES (gas check: 553 shares = $482 trades), so its "$/day" column was neither dollars nor 0.5 x dollars. This redo uses trades only.
* Its top 17 were almost all sports (soccer, MLB, UFC), which this project excludes; none appear here.
* It measured only the emergence time of the winner, with no price paid or depth, so it could not produce a $/day figure; this table has both.

Confidence 6/10. To reach 9: decision-time own-token books for >= 20 events in each of the top 10 families (IT row), and 40-event samples for the 15-minute series (only 1-2 days of tapes now).
