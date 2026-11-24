# Nautilus paper spec: LATE-RESOLVING wti-up-or-down-15m (R-078 item 3), draft for the audit gate, 24 Nov 2026

Labels on every $: **SIM** = Nautilus fill-model result (none exists yet), **FLOOR** = backtest with fills capped at printed size, **UNPROVEN** = interval or sample does not settle it. Every number in section 2 is FLOOR and UNPROVEN. Paper only; runs on Prime (R-039). Confidence 6/10.

## 1. Contract facts (live gamma read 24 Nov ~03:00Z, event "WTI Crude Oil Up or Down - November 23, 9:45PM-10:00PM ET")
* One event = one 15-minute window, 96 a day (92 open now), two tokens Up and Down (separate own-token books, never 1 minus the other side).
* Resolves Up if the Chainlink US Oil stream mid (NY-USOIL/USD-Streams-FuturesPrice) at the end is >= the mid at the start of the window. The start price is known 15 minutes before the end; this is the public input.
* `secondsDelay` null; SETTLED fact 3: non-weather markets hold marketable orders 250 ms. `feeSchedule` rate 0.01, exponent 1, takerOnly true, rebateRate 0.2, `feeType` crypto_fees_v2; fee per share = 0.01 x p x (1-p) taker, rebate not assumed. `orderMinSize` 5 shares, tick 0.01.

## 2. Evidence basis (FLOOR, UNPROVEN): pipeline/late_leader.py, commit 3364acc6d3, table `late_leader_table.csv` row wti-up-or-down-15m
* Rule tested: at T-5 min buy the own-token leader (highest own last print) at the earliest BUY print within 10 min (not after the end), size = printed BUY $ up to $200, hold. 38 events (2.4 days of tapes, to 19 Nov 03:45Z), 11 bets, 9 won (82%) at an average price of 0.52, $9.00 average stake (print-capped), +$70 on $99 notional (ROI 71%), **+$29.05/day, 95% lower bound +$5.52/day**. T-10 min: +$21.74/day (14 bets); T-2 min: +$10.81/day (4 bets). Hindsight ceiling $41.98/day.
* Why UNPROVEN: 11 bets; 1 of 81 families screened (5 had a lower bound above 0, about 2 expected by chance); the same rule on gold and silver 15m was -$106/day to +$23/day with lower bounds -$97 to -$85; the stake is $9 so $29/day is not capacity: a $100-150/day target needs the edge to hold at about $1,000+ of notional a day, and a 71% ROI on 11 bets is a tail draw, not a plan.

## 3. Pre-registered rule (information set at decision time only; MODELLING-PRINCIPLES 8)
Arm A (primary): t = end - 5 min. Candidates = both tokens of the event. Leader = highest own best bid among tokens with a two-sided book. Skip if the leader bid >= 0.90 (decided) or the book is one-sided. Enter a marketable buy at the leader's own best ask if ask <= 0.85 and ask <= leader bid + 0.04. Size = min($200, 50% of own ask depth within ask+0.02), at least 5 shares; $2,000/day cap on fills. Hold to resolution, no exit. Arms B (T-10 min) and C (T-2 min) run in the same paper process with the same rule; all three are registered now, none chosen after the fact.
Fill model (Nautilus): order released at t, matched at t + 250 ms against the own-token ladder recorded at that time (walk the ladder, no queue); fee 0.01 x p x (1-p) per share; no maker rebate; no partial-fill optimism (unfilled remainder is dropped).

## 4. Sequential stop rules (MODELLING-PRINCIPLES 13)
Per arm, per bet i the return per $ x_i (bounded in [-1, 1/p-1]). Always-valid 95% confidence sequence for the mean (hedged betting, Waudby-Smith and Ramdas; alpha 0.05/3 per arm for three arms). SUCCESS: lower bound > 0.02 (cost margin) and measured-depth $/day lower bound >= $20. FUTILITY (formal "dead"): upper bound < 0.02 AND at least 100 events with MEASURED depth (SETTLED capacity rule: print-capped or unmeasured-depth results are not evidence of no edge). MAX SAMPLE: 400 events (about 25 days at 15.7 events/day): then "inconclusive, ranked".

## 5. Capacity (MODELLING-PRINCIPLES 14, SETTLED capacity rule)
Report per arm: median and 10th percentile of own-token ask depth within +2c at decision time, fills/day, $ edge/day at that depth, share of the $200/day bar. Measured depth source: resolving-books recorder (P127) with `wti-up-or-down-15m` at T-10m/T-5m/T-2m, plus the Nautilus process's own L2 log. No $/day claim before 100 measured events.

## 6. Gaps filed 24 Nov ~03:00Z (R-078 confirm by 06:00Z)
* **wti-15m was NOT in P127's universe**: my series list excluded `-15m` series and the recorder only used 3 h / 1 h / 30 min leads. Fixed in commit (this branch): `wti-up-or-down-15m` added to `it/resolving_books_series.txt`, `leads_for()` gives 15m series T-10m/T-5m/T-2m, 16 tests pass, preflight PASS (35 series, 614 expected tokens). P127 must be restarted on that commit; until IT posts a health read that includes wti-15m rows, it is NOT RECORDED.
* P127's own health read was not in the reviewer tree when I looked (only R-078 mentions it); I cannot paste it and will not describe it.
* The Nautilus L2 recorder for the paper arms does not exist yet: needs the live CLOB WebSocket subscription per open wti-15m event. Expected write: UNMEASURED until the 60 s R-058 preflight; budget 50 MB/day.

## 7. R-058 pre-flight (before any start, run by IT on Prime)
Subscribed tokens > 0 and equal to the expected count (2 per open wti-15m event); single-instance lock (second copy refused); health checker supports the mode (`resolving_books.py health` for the recorder; the Nautilus process needs its own check: rows/min per token >= 1); 60 s of real live L2 written to disk. Any FAIL: nothing starts.

## 8. What kills it
Chainlink stream gaps or the Down default if no price is published; 250 ms hold re-quoting the book before the fill; depth under $20 per bet at the decision price (then capacity-limited and stackable only); the 2.4-day sample being a tail draw.
