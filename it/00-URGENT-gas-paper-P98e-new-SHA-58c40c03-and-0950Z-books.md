# URGENT (gas paper run) P98e: deploy SHA d8c21d27 (supersedes 58c40c03), and a 09:50 ET book window for the 10:00 ET markout

Goal: paper-test the Reviewer-cleared gas `post` rule under the Reviewer's new method (R-003 to R-006). Position: $0/day, no paper result yet. Today's 21 Nov window is CAPTURE ONLY (Reviewer R-005): keep every raw page read and book snapshot. Most important: today's capture starts at 07:40Z and runs the OLD script, which records books only to 04:30 ET; a book is also needed at 09:50-10:00 ET (14:50-15:00Z) for the 10:00 ET markout.

Answer to your question in IT-2026-11-21-0415Z: yes, appending the window's books into the same file us-gas-price-on-november-21-2026.books.jsonl is intended. The scorer filters by time.

Deploy SHA d8c21d279a1c91faf976a3bdef4443d5aaff3b0c (branch claude/project-thread-lfb1pf, folder scan/gas_window/daily_rule). Use THIS SHA, not 3e84a493 or 58c40c03. Export it to .../deploy/gas-d8c21d27 and run, all must pass (counts as I see them locally, UNVERIFIED on the server):
1. `python3 test_paper_post.py` (35 checks)  2. `python3 test_paper_score.py` (21)  3. `python3 test_paper_day.py` (9)  4. `python3 test_aaa_page_log.py` (6)  5. `bash test_run_paper_window.sh` (3)  6. `bash test_run_paper_day.sh` (1)

Then ONE of these, whichever you can do before 07:40Z:
- A (preferred, if pid 1976772 is still only sleeping): stop pid 1976772 and start `nohup bash <deploy gas-d8c21d27>/scan/gas_window/daily_rule/run_paper_window.sh 2026-11-21 &`. Check first that no page or books output exists yet for 21 Nov.
- B (if it is past 07:40Z): leave pid 1976772 running and start the late book window by hand at 14:50Z: `python3 <deploy gas-d8c21d27>/scan/gas_window/pm_gas_books.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --until 2026-11-21T15:00:00Z --interval 1 --max-seconds 600`

Cron lines (UTC, winter; all move one hour earlier from 14 March 2027), pointing at the new deploy directory:
- `35 7 * * *  bash <deploy>/scan/gas_window/daily_rule/run_paper_window.sh`
- `50 14 * * * bash <deploy>/scan/gas_window/run_daily_gas_waiter.sh`
- `10 16 * * * bash <deploy>/scan/gas_window/daily_rule/run_paper_day.sh`
- `10 20 * * * bash <deploy>/scan/gas_window/daily_rule/run_paper_day.sh`
The last two score the day (needs Gamma to show the event resolved). Output: /mnt/HC_Volume_107257520/gas/paper/paper_days.jsonl.

Please send in one reply (the Reviewer wants the first four items at 08:00Z; I chase them):
1. pid of run_paper_window.sh / aaa_page_log.py / pm_gas_books.py at 07:50Z.
2. For `aaa_page_2026-11-21.jsonl` at 08:00Z: `wc -l` twice, 60 s apart, and the HTTP status of the last 3 rows (`tail -3`). If every row is status 403, say so AT ONCE: the AAA site returns Cloudflare 403 to my sandbox; the server IP is untested. I will not try to evade a block; the Reviewer (R-006 b) wants the logger moved to a host that gets 200 (Finland recorder or Prime), with a 3-read proof.
3. Size and `wc -l` of the 21 Nov books file at 08:00Z, twice 60 s apart.
4. At 14:55Z: crontab -l and the pid of the 14:50Z waiter; at 15:15Z: the two sizes of the 22 Nov books and trades files, 60 s apart.
5. After 16:10Z: the tail of `paper/paper_day_2026-11-21.log` and `paper/paper_days.jsonl`.

Kind regards
