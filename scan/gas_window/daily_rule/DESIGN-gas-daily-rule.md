# Gas daily rule: design and pre-registration (20 Nov 2026, 01:55Z). PAPER RUN NOT STARTED: waits for a Reviewer note that clears it.

Goal: small, repeatable daily profit on the US gas price series (Polymarket now, Kalshi KXAAAGASD later as model/benchmark only, SETTLED A6), toward $500/day. No orders are ever sent (A7). Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.

## Structure (so a Kalshi adapter can plug in)
- Model: `scan/gas_window/nowcast.py` (nowcast v0: ridge alpha 10, spot_lag 2, trained from 26 Mar). Output per event: mean and sd of the AAA print for day D, from information known at listing. Bucket probabilities q_j are Normal over the listed edges, renormalised.
- Rule: `rule.py`, pure (no I/O, no venue names). Input: win probability q of one token, one displayed ask (price, size), spent so far. Output: shares.
- Adapter: Polymarket only so far. Backtest adapter = recorded taker BUY prints treated as liftable asks (`backtest.py`). Live paper adapter (not built) = recorded 12-token books from `pm_gas_books.py` at 1 s plus `pm_gas_trades.py`. A Kalshi adapter would map KXAAAGASD markets to the same bucket list and quotes.

## The three rules (windows do not overlap)
1. `yes_fav` (PRE window: listing to 03:00 ET on D): YES of the bucket with the highest q, only when ask <= q - 0.05 (gap from DESIGN-amendment-2, PR 447).
2. `no_out` (PRE window): NO of every bucket with q <= 0.02 (ruled out), only when q_no - ask - fee per share >= 0.005, i.e. asks of about 0.97 to 0.985.
3. `post` (from 03:30 ET on D, after the AAA page update at about 03:15 ET): with the AAA page value read, YES of the bucket containing it and NO of every other bucket, only when 0.995 - ask - fee >= 0.003 (0.995 = ASSUMED 0.5% risk that the page differs from the 10:00 ET resolution reading).
03:00 to 03:30 ET is skipped (no inference around the update).

## Sizing and costs
Quarter Kelly: stake target = 0.25 * bank * (q - p)/(1 - p) per token, taken only from displayed ask size (print size in the backtest). Fee = 0.04 * p * (1 - p) per share on takers (Gamma feeSchedule; Finance coefficient becomes 0.05 from 20 Nov 23:59 UTC: re-run). Bank = $1,000 (ASSUMED, paper). Caps on total cost per event: v1 one shared 15% of bank; v2 per rule yes_fav 10%, no_out 5%, post 10%.

## What was chosen before looking at results, and what was not
Before: rule structure, the 0.05 gap, quarter Kelly, the three windows, out_q 0.02, min edges. The NO and post results were NOT known when `rule.py` v1 was written.
After one look: v2 per-rule caps (v1 let one NO fill of $150 for a $1.5 gain starve the YES rule on 25 Oct). Both are reported. v2 is therefore a post-hoc choice and needs the forward test.

## Backtest (35 events 16 Oct-19 Nov, no hindsight in selection, upper bound on fills)
Run with `python3 backtest.py` (tape and AAA values in /mnt/project-files/gas/data/, hashes in the REPLY). Planted tests: `test_rule.py` 5 of 5, `test_backtest.py` 4 of 4.
Known weaknesses: fills are print-size upper bounds (no queue, no latency); `post` rests on the 03:30 ET read assumption and on page/resolution agreement; `yes_fav` profit comes from 3 days; 35 events; one nowcast parameter set; ruled-out bucket win rate 1 of 70.

## Acceptance to start paper (Reviewer sign-off required) and to keep going
Paper means: log the rule's hypothetical fills against the recorded live books each night, send nothing. Keep a rule only if after 20 forward events: `post` net > 0 with at least 10 days traded and a hit rate of at least 95%; `no_out` net >= 0; `yes_fav` net > 0 and not more than 60% from its best 2 days. Otherwise drop that rule. Stop everything if a ruled-out bucket wins on 2 of the first 20 events.
