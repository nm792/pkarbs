# SPEC: macro stale-quote pickoff, Nautilus paper (R-077 A, R-078 item 2). 24 Nov 2026, re-audit thread. Paper only, no orders.

1. **Goal:** reliably $200/day automated Polymarket edges, stacked. **Where this stands:** no MEASURED figure. Basis is a FLOOR of $8-38/day (print-sized trades in the 26 Oct macro scan; $38/day at 30% capture ex-largest day, $8-21 for a 1-3 s bot; 41% of profit from one FOMC day). **The item that matters most:** the first capture (Core PCE, Wed 25 Nov 13:30Z) decides whether stale asks persist after the print at all, and it needs no news feed to measure that.

## 1. SETTLED and market facts used (each read, not assumed)
| fact | value | source |
|---|---|---|
| Own-token books | YES and NO are separate books; price each token from its own asks; never NO = 1 - YES | SETTLED A1 |
| Taker hold | per market `seconds_delay` from CLOB `/markets/<condition_id>`. **Core PCE markets read 0 s on 24 Nov ~03:20Z** (7 of 7 checked market 1; recorder stores it for all 14). Not the 250 ms of A3; 1 s on sports (R-065) | clob.polymarket.com/markets, 24 Nov 03:20Z; R-065 |
| Fee | per market `feeSchedule`: PCE `{exponent 1, rate 0.01, takerOnly true, rebateRate 0.25}`, so fee/share = 0.01 x p x (1-p) at most 0.25c (UNVERIFIED against the docs' formula; recorder stores the schedule per market) | Gamma `/events?slug=`, 24 Nov 03:20Z |
| Minimum size | `orderMinSize` 5 shares; tick 0.001 | Gamma and CLOB, same read |
| Volume reality | Gamma `volume24hr` on one PCE bucket = $55 (24 Nov ~03:20Z); event volumes $27K (MoM) and $43K (YoY) lifetime. Depth is unknown until recorded | Gamma |

## 2. Universe and capture (recorder it/pm_event_books.js, SHA-256 178a2102e4b117a7...)
Both tokens of every market of the named events, ms `recv_ms` timestamps on one local clock, window T-30 min to T+30 min, top 3 levels, a row on every best bid/ask or size change. Releases (Gamma 24 Nov): Core PCE MoM + YoY Oct, **Wed 25 Nov 13:30Z (first target)**; Nov jobs + unemployment, Fri 4 Dec 13:30Z; Fed decision Dec statement, Wed 9 Dec 19:00Z (verify on the Fed calendar); Nov CPI Thu 10 Dec 13:30Z. Recorder confirmed by a pre-flight (container: 14 markets, 28/28 tokens, 136 rows in 60 s, PASS) and, before each release, an IT health read pasted in INBOX (R-037 bars: >= 99% snapshots, 0 errors, own-token field `asks`/`bids` of the traded token, disk, pid).

## 3. Decision rule (frozen now, before any data)
At t_dec = R + L (L = our latency from the official print; **L is UNKNOWN: no fast print source is chosen**, so the scorer is run for L = 0.5, 2, 5, 15 s) the released number is known, hence the winning token of each bucket (mapped from the PRINT into `winners.json`, never from settlement). Buy that token at its own best ask if the ask is below 0.95, size min(level size, $200/price), per-day cap $2,000. The order lands at t_dec + `seconds_delay`. It fills only if the same level is still shown with >= 5 shares in the last book row at or before the landing time; else logged `unfilled (hold)`. A market with unknown `seconds_delay` is REFUSED. Code: it/macro_pickoff_score.py (SHA-256 967a69189935f26e...).
Nautilus build (after the first capture, not before): a strategy that subscribes to order-book deltas for the tokens of the next release, takes the print from the chosen source, and sends one FOK/limit buy at the decision ask in paper mode; every parameter above is read from the market, none hard-coded.

## 4. What is measured first (needs no feed, answers "is there anything to pick off")
1. **Time to reprice:** per bucket, seconds from R to the first row where the winning token's own ask is >= 0.95 (winner from settlement, a measurement only, not a decision input). If the median is under about 1 s, a retail-speed bot has nothing; if it is tens of seconds, L of 5-15 s is viable.
2. **Stale depth:** own-token ask depth in $ at prices <= 0.90 at R+0.5, R+2, R+5, R+15 s, per bucket.
3. **Control (MODELLING-PRINCIPLES 8, 13):** the same ask at R-20 min and R-1 s. If asks are as cheap at R-20 min as at R+L, the "stale" ask is old mispricing, not a post-print stale quote; compare the two.

## 5. Tests and controls (all built, passing)
`it/test_macro_pickoff_score.py` 9 checks, each able to fail: planted stale ask filled at the right price and size; ask pulled before arrival => `unfilled (hold)` (mutation proof: removing the hold check fails check 2); null `seconds_delay` refused; level under 5 shares unfilled; repriced ask >= 0.95 not stale; loser token never bought; no use of a book from after the decision; $2,000 cap enforced. Mutation proof 2: removing the 0.95 test fails checks 5-7. Recorder tests: `test_pm_event_books.js` 7 checks.

## 6. Sequential stops (MODELLING-PRINCIPLES 13) and capacity (14), pre-set
- Unit = one release. There are only about 3-4 listed US releases per month, so **power is very low**: a 95% lower bound above 0 on per-release P&L needs the SD, which does not exist yet; it is estimated from the first 3 releases and written into the INBOX before release 4. Labels stay UNPROVEN until then.
- **Futility stop:** after 6 releases, stop if cumulative P&L at the best L is <= 0 or if the winner ask is already >= 0.95 at R+L in at least 80% of buckets.
- **Success stop (ranked, not a pass):** lower 95% bound on mean per-release P&L > 0 with at least 8 releases and top release under 40% of total.
- **Capacity:** fills use recorded depth at $200 per trade, cap $2,000/day. Converting to $/day: the basis FLOOR $8-38/day equals about $60-300 per release at 3-4 releases a month, so a $100-150/day claim (Nick, 02:53Z) would need about $800-1,500 per release; that is possible only if recorded stale depth at PCE or CPI buckets exceeds it. **Not claimed.**
- Every $ in this document: SIM or FLOOR or UNPROVEN. Nothing is MEASURED until a release is captured and scored.

## 7. Open gaps (named, not hidden)
No fast print source (BLS/BEA site read, wire or other) is chosen or timed, so L is unknown. The fee formula needs the docs check. Release times for FOMC need verification. The 26 Oct FLOOR was built from print sizes on the earlier PM macro markets, not on these PCE/jobs/CPI contracts.
