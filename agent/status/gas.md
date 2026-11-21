## Gas waiter install (20 Nov)

- Code source: `0e113601dc1bad5a763b318044c9066002ce5ae6` on `claude/project-thread-lfb1pf`; exported to `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-0e113601`.
- Tests on the exact source: `test_wait_listing.py` — 2 of 2 pass; `test_pm_gas_trades.py` — 2 of 2 pass; `test_gate_boundary.py` — 5 of 5 pass. The two simulated poll-reset messages were expected test cases; each suite passed.
- VOL2 free space at install check: 11,302,965,248 bytes (above the 10 GB floor). Output directory `/mnt/HC_Volume_107257520/gas` exists.
- Installed Prime crontab entry: `50 14 20 11 * cd /mnt/HC_Volume_107257520/pkarbs/deploy/gas-0e113601 && python3 scan/gas_window/wait_listing.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --wait-until 2026-11-20T16:30:00Z --record-seconds 5400 > /mnt/HC_Volume_107257520/gas/wait-20261121.log 2>&1`.
- The one-shot is scheduled for 14:50Z today. The waiter has not run yet; PID, listing detection and output growth are not yet verified.

## Gas waiter run (20 Nov)

Read-only proof at 2026-11-20 16:42:13Z and 16:43:14Z (60 seconds apart):

- `pgrep -af wait_listing`: no matching process output at either reading.
- First `ls -l`: `us-gas-price-on-november-21-2026.books.jsonl` was 27,109,015 bytes, mtime Nov 20 16:29; `us-gas-price-on-november-21-2026.trades.jsonl` was 19,815 bytes, mtime Nov 20 16:15.
- Second `ls -l`: both files had the same sizes and mtimes; neither grew during the interval.
- `tail -5 wait-20261121.log` returned three lines: `LISTED after 1800 polls`; `new trades 22 errors 0`; `polls 5097 errors 0 file /mnt/HC_Volume_107257520/gas/us-gas-price-on-november-21-2026.books.jsonl`.
- Both output files and the log were present; no missing-file condition.


## Gas paper window (21 Nov 2026)

- Source commit: `3e84a493aaf12f1f86e12cdb1f6d1d3ca5c3a594` on `claude/project-thread-lfb1pf`; the deployed `run_paper_window.sh` SHA-256 matches that source (`5c92f968285e0800243e14b3758d0e1c22fbb0615edb38a14e3d61de95809360`).
- Selected `/mnt/HC_Volume_107257520/mfw-venv/bin/python` (Python 3.14.4, numpy 2.5.3); no environment or package was changed.
- Tests on the exact deployed source: `test_paper_post.py` — all pass (28 checks; `ALL PASS 0`); `test_aaa_page_log.py` — all pass (6 checks; `ALL PASS 0`); `test_run_paper_window.sh` — 3 of 3 pass.
- Pre-start snapshot saved at `/mnt/HC_Volume_107257520/gas/paper_window_20261121.prestart-20261121T0612Z.txt` at 2026-11-21 06:13:09Z: listing JSON (403 bytes), books file (27,109,015 bytes, 5,097 lines; head and tail included). Original source files were not changed.
- Started `run_paper_window.sh 2026-11-21` at 2026-11-21 06:13:19Z. PID 1976772 was verified running from the deploy directory; the script is sleeping in its own wait loop for the 07:40Z window. Its outer log is currently empty, as expected before the window; capture output has not yet been verified. No live orders were sent.
- State: test gate passed and the scheduled paper-window process is running; window capture is pending its 07:40Z start.
