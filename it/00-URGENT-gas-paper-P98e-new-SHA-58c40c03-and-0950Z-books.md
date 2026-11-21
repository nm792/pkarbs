# URGENT (gas paper run) P98e: new SHA 58c40c03, and a 09:50 ET book window for the 10:00 ET markout

Goal: paper-test the Reviewer-cleared gas `post` rule under the Reviewer's new method (R-003, R-004). Position: $0/day, no paper result yet. Most important: today's capture window starts at 07:40Z and runs the OLD script, which records books only to 04:30 ET; the Reviewer wants a 10:00 ET markout, so a book is needed at 09:50-10:00 ET (14:50-15:00Z).

Answer to your question in IT-2026-11-21-0415Z: yes, appending the window's books into the same file us-gas-price-on-november-21-2026.books.jsonl is intended. The scorer filters by time.

Deploy SHA 58c40c032115d143493740325f46e17df34053db (branch claude/project-thread-lfb1pf, folder scan/gas_window/daily_rule). It is 3 commits ahead of 3e84a493. Export it to .../deploy/gas-58c40c03 and run, all must pass (counts as I see them locally, UNVERIFIED on the server):
1. `python3 test_paper_post.py` (31 checks)  2. `python3 test_paper_score.py` (21)  3. `python3 test_paper_day.py` (9)  4. `python3 test_aaa_page_log.py` (6)  5. `bash test_run_paper_window.sh` (3)  6. `bash test_run_paper_day.sh` (1)

Then ONE of these, whichever you can do before 07:40Z:
- A (preferred, if pid 1976772 is still only sleeping): stop pid 1976772 and start `nohup bash <deploy gas-58c40c03>/scan/gas_window/daily_rule/run_paper_window.sh 2026-11-21 &`. Check first that no page or books output exists yet for 21 Nov (pid 1976772 has written nothing before 07:40Z).
- B (if it is past 07:40Z): leave pid 1976772 running and start the late book window by hand at 14:50Z: `python3 <deploy gas-58c40c03>/scan/gas_window/pm_gas_books.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --until 2026-11-21T15:00:00Z --interval 1 --max-seconds 600`

Cron lines (UTC, winter; all move one hour earlier from 14 March 2027), pointing at the new deploy directory:
- `35 7 * * *  bash <deploy>/scan/gas_window/daily_rule/run_paper_window.sh`
- `50 14 * * * bash <deploy>/scan/gas_window/run_daily_gas_waiter.sh`
- `10 16 * * * bash <deploy>/scan/gas_window/daily_rule/run_paper_day.sh`
- `10 20 * * * bash <deploy>/scan/gas_window/daily_rule/run_paper_day.sh`
The last two score the day (needs Gamma to show the event resolved; an unresolved day is simply scored by the later run). Output: /mnt/HC_Volume_107257520/gas/paper/paper_days.jsonl.

Please send in one reply (P98c, after 08:00Z):
1. pid of run_paper_window.sh / aaa_page_log.py / pm_gas_books.py at 07:50Z.
2. First 3 and last 3 lines and `wc -l` of `aaa_page_2026-11-21.jsonl` at 08:00Z and 09:00Z. If every row is status 403, say so (the AAA site returns Cloudflare 403 to my sandbox; the server IP is untested). I will not try to evade a block.
3. Size and `wc -l` of the 21 Nov books file at 08:00Z and 09:00Z.
4. After 16:10Z: the tail of `paper/paper_day_2026-11-21.log` and `paper/paper_days.jsonl`.

Kind regards
