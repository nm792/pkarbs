# 00-URGENT for IT: deploy 888269b2 (replaces 20293df7), before 07:35Z 22 Nov 2026

Reviewer R-020 found that decision time must be the page RESPONSE time. Fix is in commit 888269b2f84245d39abf1fc7ebf7dcaccdb59b75 (branch claude/project-thread-lfb1pf, dir scan/gas_window/daily_rule). Paper only, no orders.

1. Export exactly 888269b2 to `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-888269b2`, point the 16:10Z and 20:10Z scorer crons (and the 07:35Z capture) at it, and paste the output of: `test_paper_post.py` (43 checks), `test_paper_score.py`, `test_paper_day.py`, `test_aaa_page_log.py`, `test_aaa_page_tinyfish.py` (8 checks), `test_run_paper_window.sh`, `test_run_paper_day.sh`.
2. The AAA page source for 22 Nov is the TinyFish monitor (R-019), not a server logger: you do NOT need a TinyFish API key and need not run `aaa_page_tinyfish.py`. The old direct logger keeps writing 403 rows; leave it (403 rows are the record). The converted monitor rows will be committed by the gas thread after the window as `aaa_page_2026-11-22.tinyfish.jsonl`; paper_day reads that file.
3. Book logger: window starts 07:40Z (cron 07:35Z). Post the pid and the books file size twice 60 s apart before 07:50Z, and the 15-minute sanity (books rows growing, page rows) before 08:30Z, in agent/status/gas.md.
