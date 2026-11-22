# URGENT (gas paper run): start the paper capture window at 07:40Z today, and install two daily crons

Goal: paper-test the Reviewer-cleared gas `post` rule (R-002, reviewer e5648c5e). Position: $0/day; the paper run has produced nothing yet because no book was recorded at the AAA page change (03:15 ET). The listing waiter only records 15:00-16:30Z, so a SECOND capture window is needed: 02:40-04:30 ET on the event day. Most important item: start it TODAY at 07:40Z (Hello, please send in one reply: the pid at 07:45Z).

Deploy SHA 3e84a493aaf12f1f86e12cdb1f6d1d3ca5c3a594 (branch claude/project-thread-lfb1pf, folder scan/gas_window). Tests, run first, all must pass:
1. `python3 scan/gas_window/daily_rule/test_paper_post.py` (28 checks)
2. `python3 scan/gas_window/daily_rule/test_aaa_page_log.py` (6)
3. `bash scan/gas_window/daily_rule/test_run_paper_window.sh` (3)

Run (the script waits for 07:40Z itself, so start it any time before):
`nohup bash <deploy>/scan/gas_window/daily_rule/run_paper_window.sh 2026-11-21 &`
It writes to /mnt/HC_Volume_107257520/gas: `aaa_page_2026-11-21.jsonl` (one row every 30 s, includes HTTP errors), `us-gas-price-on-november-21-2026.books.jsonl` (1 s), logs `aaa_page_2026-11-21.log`, `paper_books_2026-11-21.log`.

Cron lines (UTC, winter; both move one hour earlier in US summer time from 14 March 2027):
- `35 7 * * * bash <deploy>/scan/gas_window/daily_rule/run_paper_window.sh`   (event day = today UTC)
- `50 14 * * * bash <deploy>/scan/gas_window/run_daily_gas_waiter.sh`   (SHA 93fec9ed or later; already asked in REPLY-2026-11-21-0255Z)

Please send in one reply:
1. `ps` line with pid of run_paper_window.sh / aaa_page_log.py / pm_gas_books.py at 07:45Z.
2. First 3 and last 3 lines of `aaa_page_2026-11-21.jsonl` at 07:55Z, and `wc -l`. If every row shows status 403, say so: the AAA site blocks my sandbox with Cloudflare (cf-ray IAD); the server IP is untested. I will not try to evade a block; the paper day then counts as UNSOURCED for the page.
3. `ls -l` and `wc -l` of the books file at 08:00Z and 09:00Z.
4. `crontab -l` showing both lines.
5. For the 20 Nov run: `us-gas-price-on-november-21-2026.listing.json` and the first and last line of its books file (needs the detect time).
6. The root cause of the agent stalls (see REPLY-2026-11-20-0412Z).

Kind regards
