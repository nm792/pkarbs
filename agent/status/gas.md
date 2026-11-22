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
## Gas deploy 20293df7 / P98e (21 Nov 2026)

- Source: `20293df7f1195e8c17956f2abd963b6327f4ef14` from `claude/project-thread-lfb1pf`; exported to `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-20293df7` (53 files). Python: `/mnt/HC_Volume_107257520/mfw-venv/bin/python`, 3.14.4 / numpy 2.5.3.
- Tests on deployed source: `test_paper_post.py` 41 checks, `test_paper_score.py` 21, `test_paper_day.py` 10, `test_aaa_page_log.py` 6, `test_run_paper_window.sh` 3/3, `test_run_paper_day.sh` 1/1; all passed.
- Four crontab entries installed at 11:15Z, with PATH set to the tested Python environment: 07:35 capture; 14:50 waiter; 16:10 and 20:10 scorer. Pre-edit crontab: `/mnt/HC_Volume_107257520/pkarbs/deploy/crontab.pre-P98e-20261121T111505Z`.
- Late-books runner is staged at `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-20293df7/start_late_books.sh`, syntax-checked; background session `proc_cb4baa47f8c5`, PID 2259571, is waiting to run the 14:50–15:00Z capture. It must be verified after its window.
- The first attempted sleeper referenced a nonexistent deployment path; it was terminated after verifying its command line. The replacement runs the actual VOL2 deploy path. No capture was lost or overwritten.
- No live orders. Current AAA log is returning HTTP 403; see P98c.

## P98c Gas paper-window read-only check (21 Nov 2026)

- At 11:16:27Z, PID 1976772 was absent. The running `aaa_page_log.py` was PID 2053710 from deploy `gas-3e84a493`; no `run_paper_window.sh` or `pm_gas_books.py` process was present at the check.
- AAA page log `/mnt/HC_Volume_107257520/gas/aaa_page_2026-11-21.jsonl`: 433 lines at 11:16:27Z and 435 at 11:17:28Z. First and last three rows all showed HTTP 403; latest row time 11:17:03Z. The live logger is continuing to append 403 rows, with no prices.
- Books file `/mnt/HC_Volume_107257520/gas/us-gas-price-on-november-21-2026.books.jsonl`: 63,760,708 bytes and 11,693 lines at both reads; mtime 09:29:59Z. No growth across the 61-second check.
- `paper_books_2026-11-21.log` tail: `polls 6596 errors 0`; no error count at that read.
- 21 Nov remains capture-only. The late 14:50–15:00Z book window is staged separately under P98e and has not yet run.


## Gas deploy 20293df7 / P98e (21 Nov 2026)

- Source: `20293df7f1195e8c17956f2abd963b6327f4ef14` from `claude/project-thread-lfb1pf`; exported to `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-20293df7` (53 files). Python: `/mnt/HC_Volume_107257520/mfw-venv/bin/python`, 3.14.4 / numpy 2.5.3.
- Tests on deployed source: `test_paper_post.py` 41 checks, `test_paper_score.py` 21, `test_paper_day.py` 10, `test_aaa_page_log.py` 6, `test_run_paper_window.sh` 3/3, `test_run_paper_day.sh` 1/1; all passed.
- Four crontab entries installed at 11:15Z, with PATH set to the tested Python environment: 07:35 capture; 14:50 waiter; 16:10 and 20:10 scorer. Pre-edit crontab: `/mnt/HC_Volume_107257520/pkarbs/deploy/crontab.pre-P98e-20261121T111505Z`.
- Late-books runner is staged at `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-20293df7/start_late_books.sh`, syntax-checked; background session `proc_cb4baa47f8c5`, PID 2259571, is waiting to run the 14:50–15:00Z capture. It must be verified after its window.
- The first attempted sleeper referenced a nonexistent deployment path; it was terminated after verifying its command line. The replacement runs the actual VOL2 deploy path. No capture was lost or overwritten.
- No live orders. Current AAA log is returning HTTP 403; see P98c.

## P98c Gas paper-window read-only check (21 Nov 2026)

- At 11:16:27Z, PID 1976772 was absent. The running `aaa_page_log.py` was PID 2053710 from deploy `gas-3e84a493`; no `run_paper_window.sh` or `pm_gas_books.py` process was present at the check.
- AAA page log `/mnt/HC_Volume_107257520/gas/aaa_page_2026-11-21.jsonl`: 433 lines at 11:16:27Z and 435 at 11:17:28Z. First and last three rows all showed HTTP 403; latest row time 11:17:03Z. The live logger is continuing to append 403 rows, with no prices.
- Books file `/mnt/HC_Volume_107257520/gas/us-gas-price-on-november-21-2026.books.jsonl`: 63,760,708 bytes and 11,693 lines at both reads; mtime 09:29:59Z. No growth across the 61-second check.
- `paper_books_2026-11-21.log` tail: `polls 6596 errors 0`; no error count at that read.
- 21 Nov remains capture-only. The late 14:50–15:00Z book window is staged separately under P98e and has not yet run.

## P98d gas waiter live proof (22 Nov 2026; checked 02:26–02:30Z)

- The 22 Nov waiter completed: its log records `LISTED after 1800 polls`, 5,097 polls with 0 errors, and 14 new trades with 0 errors. Books: 5,097 rows / 27,315,735 bytes, receive times 15:05:00Z–16:29:59Z on 21 Nov. Trades: 14 rows / 12,607 bytes, receive times 15:10:01Z–16:05:04Z. Both file sizes were unchanged across a 60-second recheck.
- PID 2259571 was absent. The requested `late_books_20261121.nohup` and expected `paper_books_late_2026-11-21.log` were absent; no late-books output was found.
- The 21 Nov page log has 880 rows, all HTTP 403, from 07:40:03Z through 14:59:33Z. The 21 Nov scorer therefore recorded `page_log_ok=false`, `days_scored=0`; this is not a 22 Nov result.
- At 02:26Z the 22 Nov books and trades were available to the 16:10Z and 20:10Z scorer crons, but the 22 Nov page input had not yet been created (its 07:40Z capture is in the future). Those scorer runs are not yet verifiable.
- Evidence paths: `gas/us-gas-price-on-november-22-2026.books.jsonl`, `gas/us-gas-price-on-november-22-2026.trades.jsonl`, `gas/wait-20261122.log`, `gas/aaa_page_2026-11-21.jsonl`, and `gas/paper/paper_day_2026-11-21.log`.
- Report: `agent/outbox/P98d-gas-waiter-live-proof.md`.


## Gas deploy 888269b2 / P100a (22 Nov 2026)

- Source commit: `888269b2f84245d39abf1fc7ebf7dcaccdb59b75` on `claude/project-thread-lfb1pf`; exported to the VOL2 deployment `gas-888269b2`.
- VOL2 free before tests: 10,574,237,696 bytes; after tests and deployment: 10,564,354,048 bytes.
- Passed on the exact source: `test_paper_post.py`, `test_paper_score.py`, `test_paper_day.py`, `test_aaa_page_log.py`, `test_run_paper_window.sh` (3/3), and `test_run_paper_day.sh` (1/1). `test_aaa_page_tinyfish.py` was not run, as explicitly directed; no TinyFish key was needed and the direct page logger was left unchanged.
- Repointed all four recurring gas-window crontab entries from `gas-20293df7` to `gas-888269b2`; crontab readback confirms 4 new-deploy references and zero gas-window references to the old deploy. Other crontab lines were unchanged.
- No live orders.
