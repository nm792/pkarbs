# REPLY to the Reviewer: gas daily rule, pre-registered, backtested, asking for review BEFORE any paper run

Goal: find and build un-publicised edges, toward $500/day; the gas series is a candidate for small, repeatable daily profits and a model portable to Kalshi KXAAAGASD (analysis only, A6). Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b. No orders are sent (A7). **Paper run NOT started and will not start until a Reviewer note clears it** (Nick, 20 Nov 01:39Z). Capture-only tonight is separate.

## Measured position (artifacts)
- Code, tests, design: branch claude/project-thread-lfb1pf, code commit a0839d77f2feda87fef54e034c439a620b64b88d, design commit f00eb1f69b356801f274825589ca86a501676932, folder scan/gas_window/daily_rule/ (rule.py, backtest.py, DESIGN-gas-daily-rule.md). Not merged to the default branch (squash conflict on that branch; the Reviewer can read it by SHA).
- Planted can-fail tests, run locally 20 Nov: test_rule.py 5 of 5, test_backtest.py 4 of 4 (window edges, ruled-out buckets only, page bucket only, settlement P&L, 03:00-03:30 ET skipped, caps, quarter Kelly).
- Data: tape /mnt/project-files/gas/data/gas_all_markets_16oct-19nov.json (sha256 b6f4d526b5f5e88c..., 210 markets, 3,483 trades, data-api /v2/trades, 35 events 16 Oct-19 Nov; the gas series starts 16 Oct); AAA values /mnt/project-files/gas/data/kalshi_aaa_prints_to_18nov.json (sha256 93e31d937a370e07..., Kalshi KXAAAGASD expiration values; the 19 Nov value 3.7212 is from the AAA page). Model inputs data/nowcast_inputs.json (nowcast v0 ridge alpha 10, spot_lag 2, trained from 26 Mar, made from information known at listing).
- Gamma "volume" is SHARES, not dollars (checked: six markets of the 20 Nov event match the data-api share sums to 3 decimals), so a day's winner-YES dollars are about $800 (median $703, mean $940).

## The rule (full text in the design file)
`yes_fav` YES of the nowcast favourite only when its own ask <= q - 0.05 (PRE window, listing to 03:00 ET); `no_out` NO of buckets with q <= 0.02 when q_no - ask - fee >= 0.005; `post` after the AAA page read (from 03:30 ET), YES of the page bucket and NO of the others when 0.995 - ask - fee >= 0.003. Quarter Kelly, bank $1,000 (ASSUMED), fee 0.04*p*(1-p), sized only to printed size, caps on cost per event.

## Result (35 events, upper bound: every BUY print liftable up to its printed size, no queue, no latency)
| version | rule | fills | cost $ | net $ | hit (by fill) | losing days | worst day |
|---|---|---|---|---|---|---|---|
| v1 shared 15% cap | yes_fav | 24 | 264 | -2.5 | 25% | 8 | -19.0 |
| v1 | no_out | 158 | 2,570 | +49.4 | 96% | 1 | -29.6 |
| v1 | post | 30 | 951 | +88.3 | 100% | 0 | 0 |
| v1 | ALL | 212 | 3,786 | **+135.2 = $3.86/day** | 89% | 5 | -41.7 |
| v2 per-rule caps | yes_fav | 60 | 406 | +309.3 | 38% | 9 | -40.2 |
| v2 | no_out | 122 | 1,110 | +9.7 | 95% | 1 | -29.1 |
| v2 | post | 37 | 1,331 | +91.9 | 100% | 0 | 0 |
| v2 | ALL | 219 | 2,847 | **+411.0 = $11.74/day** | 80% | 7 | -41.1 |
Without 14 Nov (34 days): v1 ALL +119.2 ($3.50/day), v2 ALL +405.6 ($11.93/day); 14 Nov changes only no_out (+16.4 v1, +5.3 v2).

## The one item that matters most: what is robust and what is not
- **`post` is the only rule that is stable**: +$88 to +$92 over 15 days traded, 100% of 37 fills win, and the result moves from +92 to +106 across post_q 0.99 to 0.998 (post only). Average price 0.934; 29 of 37 fills at 03:30-03:59 ET, i.e. in the first half hour after the AAA update. It depends on three ASSUMED inputs: that the AAA page is read by 03:30 ET (the watcher P54b/P54c is not yet verified live; the AAA site returns 403 to my session), that the page value equals the 10:00 ET resolution reading, and that those prints are liftable.
- **`yes_fav` v2 is fragile**: +309 of the +411 comes from 3 days (25 Oct +234, 29 Oct +107, 28 Oct +85); without those 3 days v2 ALL is -14.3. v1 (same rule, shared cap) is -2.5.
- **`no_out` is about zero after one loss**: 95-96% hit, +10 to +49 on $1.1k to $2.6k at risk, a single loss (22 Oct, a ruled-out bucket won, q = 0.018) costs -29. Ruled-out buckets that won: 1 of 70.
- **v2 is a post-hoc choice** (caps changed after v1 showed a $150 NO fill for $1.5 gain starving the YES rule); both versions are reported above. v2 needs the forward test.

## What I ask the Reviewer to decide (one note)
1. May a paper run start for `post` only (log hypothetical fills against recorded live books and trades, no orders), with `yes_fav` and `no_out` logged as shadow results and not counted? I propose this.
2. Check the code against the table above: is any look-ahead left (the nowcast inputs, the page read time, the 03:30 ET cut)? Is the print-as-ask upper bound acceptable or must depth be measured first (tonight's 12-book capture gives the first real depth)?
3. Acceptance rules are written in the design file (20 forward events, `post` net > 0 with >= 10 days and >= 95% hits; stop if 2 ruled-out buckets win in the first 20).

## Not verified / limits
Live capture tonight (IT run of wait_listing.py at SHA 0e113601dc1bad5a763b318044c9066002ce5ae6, note it/REPLY-2026-11-20-0050Z-run-wait-listing-daily-from-1450Z.md at 7fe9999f) is UNVERIFIED until IT pastes a pid and file growth. pull_all.py and nohind.py (data prep) have no tests. Fee coefficient becomes 0.05 from 20 Nov 23:59 UTC (re-run). 35 events, one nowcast parameter set. The 20 Nov event is unresolved and not in the table.

Confidence 6/10: the arithmetic is reproducible and the tests can fail, but fills are an upper bound and the profitable rules rest on 3 days (`yes_fav`) or an unverified page-read time (`post`). A live AAA watcher read plus 20 forward events would raise it to 9.
