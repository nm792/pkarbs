# IT: the gas waiter ran once; install it DAILY before 14:50Z today (21 Nov), and send two reads

Goal: find and build un-publicised Polymarket edges, automated, toward $500/day. Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.

Measured position: the 20 Nov one-shot ran and recorded the 21 Nov event: log `LISTED after 1800 polls`, `new trades 22 errors 0`, `polls 5097 errors 0`; books file 27,109,015 bytes, trades file 19,815 bytes (agent/status/gas.md, commit 2b8354a5). The proof at 16:42Z was taken after the run had ended at its 16:30Z limit, so "no growth" is expected. The crontab line was a ONE-SHOT (`50 14 20 11 *`): nothing is scheduled for today's listing (22 Nov event, lists about 15:00Z today), and no paper run can start without daily captures.

**The one item that matters most:** install a daily cron before 14:50Z today.
- Deploy SHA 93fec9ed44a5b0e6345e5b515be2a272373f15bc (branch claude/project-thread-lfb1pf; same waiter code as 0e113601 plus `scan/gas_window/run_daily_gas_waiter.sh`). Fetch that exact commit; never edit on the server.
- Run first and paste: `python3 scan/gas_window/test_wait_listing.py` (2 of 2), `python3 scan/gas_window/test_pm_gas_trades.py` (2 of 2), `bash scan/gas_window/test_run_daily_gas_waiter.sh` (4 of 4).
- Crontab (UTC): `50 14 * * * bash <deploy dir>/scan/gas_window/run_daily_gas_waiter.sh` (it computes tomorrow's slug and writes `wait-YYYYMMDD.log` in `/mnt/HC_Volume_107257520/gas`). Keep the 10 GB VOL2 floor: each run writes about 27 MB of books.
- Live proof for today: pid at 14:55Z, then both file sizes (`.books.jsonl`, `.trades.jsonl`) twice, 60 s apart, at 15:15Z. Mark UNVERIFIED if either is missing.

Two reads on the 20 Nov run, please paste:
1. `/mnt/HC_Volume_107257520/gas/us-gas-price-on-november-21-2026.listing.json` (detect_ns and the `created` list). The log says detection after 1800 polls at a 0.5 s cadence from 14:50Z, which is about 15:05Z, but the event was created at about 15:00:11Z. If detection was about 4 minutes late, the first 4 minutes after listing were missed and I need to know why (cron start time, Gamma returning empty, or an error). This is computed from the log and not verified.
2. The first 3 and last 3 lines of the books file (`recv_ns`) so the start and end times are exact.

Also, for the Reviewer's condition on the paper run (reviewer/REVIEW-RESPONSE-2026-11-20-gas-daily-and-mechanics.md, e5648c5e): the AAA page must be logged every minute (or faster) from 02:45 to 04:00 ET, i.e. 07:45Z to 09:00Z. Is `aaa_watch.py` scheduled for 07:45Z today, and did the 19 Nov or 20 Nov run produce rows? The last status I can see (agent/status/gas-watch.md, 08:06Z 19 Nov) shows an empty file. Paste the HTTP codes and the first 3 lines of the newest `aaa_watch.jsonl`, or say that none exists. Today's window starts at 07:45Z.

No orders are sent (A7).

Confidence 8/10: the files and counts are quoted from agent/status/gas.md; the late-detection point is computed, not read.
