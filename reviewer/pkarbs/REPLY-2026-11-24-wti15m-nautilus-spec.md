# Nautilus-native live paper node: LATE-RESOLVING wti-up-or-down-15m (R-078 item 3, R-081), spec for the audit gate, 24 Nov 2026 (v2)

**Goal:** find and build un-publicised Polymarket edges that reliably deliver $500/day (bar $200/day per strategy on the CI lower bound).
**Where we stand (measured):** $0/day; the late-resolving scan has no MEASURED cell, only FLOORs: causal $53/day summed over 81 families (26% of $200) and a hindsight ceiling of $868/day (pipeline/R036-late-winner-scan-2026-11-22.md, late_leader.py 3364acc6d3, tapes to 19 Nov); wti-15m +$29.05/day, lower bound +$5.52, 11 bets, UNPROVEN.
**The one item that matters:** decision-time own-token books for these series exist nowhere until IT restarts the resolving-books recorder on commit 131c2c6200 and posts a health read; without them every $/day stays a FLOOR.


Labels on every $: **SIM** = produced by the Nautilus paper node, **FLOOR** = backtest with fills capped at printed size, **UNPROVEN** = sample or interval does not settle it. Today every $ is FLOOR and UNPROVEN; no SIM figure exists. Paper only, on Prime under IT caps (R-039). Confidence 6/10.

## 0. What is built and what is not
* **Nautilus does all fill, queue and P&L work.** The node is Nautilus live mode with paper (sandbox) execution on live Polymarket CLOB data, supervised. NO custom fill model, queue model or P&L code. Our code is only (i) the strategy class (the decision rule of section 3: reads the book, calls `submit_order`) and (ii) a reporting script that reads Nautilus's own order, fill and position reports. Fees come from the instrument/adapter fee fields; if the installed version cannot express the exponent fee, fees are subtracted in the report only (never in fill logic) and the report says so.
* Recorder P127 (`resolving_books.py`) feeds EVIDENCE only (decision-time own-token depth). It does not drive the node.
* **To confirm at pre-flight on Prime (nothing assumed):** installed Nautilus version; Polymarket instrument provider loads the `wti-up-or-down-15m` markets and both tokens; sandbox execution fills marketable orders against L2 book data from the live feed; order-book deltas arrive for both tokens. Any item that fails: the node does not start.

## 1. Known facts (each with its source)
| Fact | Value | Source |
|---|---|---|
| Contract | 15-minute window, 96 events/day (92 open on 24 Nov 03:00Z), tokens Up and Down | gamma `events/keyset?series_slug=wti-up-or-down-15m`, live read 24 Nov ~03:00Z |
| Resolution | Up if Chainlink US Oil stream mid (NY-USOIL/USD-Streams-FuturesPrice) at the end >= mid at the window start; "Down" if no price is published within 7 days; 50-50 if wrong and uncorrected | market description, same read |
| Reference price known 15 min before the end | yes (window start) | description |
| Books | YES/Up and Down are separate books of resting orders; price each token from its own book, never 1 minus the other | Nick 17 Nov rule; SETTLED A1 as amended 18 Nov |
| Taker hold | marketable orders held 250 ms on non-weather markets | SETTLED fact 3 (reviewer/SETTLED.md:13); docs.polymarket.com/concepts/order-lifecycle |
| `secondsDelay` | null on this series (sports markets only) | gamma market field, same read |
| Fees | `feeSchedule` rate 0.01, exponent 1, takerOnly true, rebateRate 0.2, feeType crypto_fees_v2: taker fee = 0.01 x p x (1-p) per share; rebate not assumed | gamma market field, same read |
| Minimum order | `orderMinSize` 5 shares; tick 0.01 | gamma market field, same read |
| Capacity rule | no $/day without MEASURED own-token depth at decision time, $200 per trade, $2,000/day cap; print-capped = FLOOR | Nick 22 Nov 05:27-05:31Z, SETTLED capacity rule |
| Pass bar | $200/day reliably, judged on the CI lower bound | SETTLED 9 (Nick 18 Nov 08:18Z) |

## 2. Evidence basis (FLOOR, UNPROVEN): `pipeline/late_leader.py` commit 3364acc6d3, row wti-up-or-down-15m
38 events (2.4 days of tapes, to 19 Nov 03:45Z). Rule: at T-5 min buy the own-token leader at the earliest BUY print in 10 min, size = printed BUY $ up to $200, hold. 11 bets, 9 won (82%) at an average price of 0.52, stake $9.00 (print-capped), +$70 on $99 notional (ROI 71%), **+$29.05/day, 95% lower bound +$5.52/day (FLOOR, UNPROVEN)**. T-10 min +$21.74/day (14 bets); T-2 min +$10.81/day (4 bets). Why UNPROVEN: 11 bets; 1 of 81 families (5 positive lower bounds, about 2 expected by chance); gold and silver 15m with the same rule had lower bounds of -$97 and -$85/day; the stake is $9, so this is not capacity. Data check 24 Nov: 40 of 40 randomly re-pulled trade tapes (/v2/trades with condition_id assertion, R-080) are identical to the cached tapes the numbers came from.

## 3. Pre-registered decision rule (what the strategy class does; information at decision time only)
At t = end - 5 min (arm A; arms B at -10 min and C at -2 min run in the same node, all three registered now, none chosen later): leader = the token with the higher own best bid among tokens with a two-sided book; skip if leader bid >= 0.90 or the book is one-sided. If the leader's own best ask <= 0.85 and <= leader bid + 0.04, submit a marketable buy through Nautilus for min($200, 50% of own ask depth within ask+0.02) shares, at least 5; $2,000/day cap; hold to resolution; no exit orders. Nautilus decides whether and how it fills (250 ms hold, book walk, queue).

## 4. MODELLING-PRINCIPLES applied
| # | Principle | How this spec applies it |
|---|---|---|
| 8 | No hindsight | Rule uses only the own books at t; arms and thresholds fixed here; leader is not the winner; no threshold chosen from outcomes. |
| 12 | Cut noise per decision | Each fill is scored by Nautilus fills at settlement AND by markout against the token's own best bid at t+10 s, t+30 s, t+60 s and window end (horizons fixed now); control variate = the Chainlink oil move since the window start. Markout is the screening and ranking statistic, settlement P&L the final check. |
| 13 | Sequential stops | Per arm an always-valid 95% confidence sequence (hedged betting, alpha 0.05/3 per arm) for mean return per $. SUCCESS: lower bound > 0.02 (cost margin) AND measured-depth $/day lower bound >= $20. FUTILITY ("dead"): upper bound < 0.02 AND >= 100 events with MEASURED depth. MAX SAMPLE 400 events (about 25 days): then "inconclusive, ranked". |
| 14 | Capacity from measured depth | No $/day claim before 100 events of MEASURED depth. Each arm reports median and 10th percentile of own-token ask depth within +2c at decision time, fills/day, $ edge/day at that depth, and the share of the $200/day bar. |

## 5. Queue position and depth: measured from the recorder
Source: resolving-books recorder (P127), series `wti-up-or-down-15m`, T-10m / T-5m / T-2m, own-token best bid, best ask, depth within +2c and +5c, `book_state`, latency. Queue position for any resting order is Nautilus's sandbox output, never ours. Status: **wti-15m was not in P127's universe** (series list excluded `-15m`; found 24 Nov ~03:00Z). Fixed in commit 1737979eb8 (series added, 15m leads); P127 must be restarted on it, then IT posts the 15-minute health read with wti-15m rows (`lead_h` 0.1667, 0.0833, 0.0333). Until then NOT RECORDED. P127's own health read was not in the reviewer tree when I looked, so I do not describe it.

## 6. R-058 pre-flight (IT on Prime, before any start; any FAIL = nothing starts)
Instruments loaded > 0 and equal to the expected count (2 tokens x open wti-15m events); single-instance lock (second copy refused); health checker supports the mode (rows per token per minute >= 1; own-token source named); 60 s of real live L2 data written to disk; Nautilus version and sandbox fill check from section 0 printed. Expected write: UNMEASURED until the 60 s pre-flight; budget 50 MB/day.

## 7. Cells in this spec family (R-086(7)): late-resolving daily stock cells, all UNPROVEN and under $3/day
Same node, same Nautilus-native design, same principles table; only the contract and the lead differ (daily contracts: arms at T-3h, T-1h primary, T-30m, because a daily contract exists for hours). Evidence is the same causal backtest (`late_leader.py` 3364acc6d3, 40 events each, tapes to 19 Nov, T-1h arm, FLOOR). Label every one UNPROVEN: 4-5 bets each, 5 positive lower bounds out of 81 families with about 2 expected by chance, 100% wins on 4-5 bets cannot support an edge claim.
| Cell (series) | Bets / events | Avg price | Won | Print-capped stake | FLOOR $/day (T-1h) | 95% lower bound | In P127 universe |
|---|---|---|---|---|---|---|---|
| nvda-daily-up-down | 4 / 40 | 0.87 | 4 | $13.86 | +0.14 | +0.01 | yes (since 01:26Z) |
| tsla-daily-up-down | 4 / 40 | 0.67 | 4 | $74.87 | +2.09 | +0.02 | added 24 Nov (restart needed) |
| whitehouse-daily-tweets | 4 / 40 | 0.90 | 4 | $140.74 | +0.29 | +0.02 | yes (since 01:26Z) |
| rklb-daily-up-or-down | 5 / 40 | 0.77 | 5 | $11.57 | +0.46 | +0.01 | added 24 Nov (restart needed) |
Stop rules and capacity rules are those of sections 4 and 5; each cell has its own 400-event cap (about 560 days at 0.71 events/day, so these cells cannot reach a verdict by waiting: they are kept for stacking only if the depth is measured and the edge appears in a pooled daily-Up/Down cell across all 40+ daily stock series). Recording is the deliverable now, not a trading claim.

## 8. What kills it
Chainlink stream gaps or the "Down" default; the 250 ms hold re-quoting the book before the fill; depth under $20 per bet at the decision price (then capacity-limited, only worth stacking); the 2.4-day sample being a tail draw.
