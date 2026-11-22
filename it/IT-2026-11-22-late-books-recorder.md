# IT TASK (deploy only): decision-time book recorder for late-resolving series, first window Sun 22 Nov 09:00Z

From the pipeline thread, for Nick's R-036 scan (due 23 Nov 12:00Z). Read-only: never places orders, no keys. Deploy committed code, run the stated commands, do not edit code. Nick does not SSH; you run everything and paste output.
Why: no order book was ever stored at the time a late-resolving contract is priced (T-3h, T-1h, T-30m before its end), so own-token ask depth near the late price cannot be MEASURED, only guessed from prints (FLOOR). Method and numbers: pipeline/R036-late-winner-scan-2026-11-22.md.

## Steps
1. `cd /mnt/HC_Volume_107257520/pkarbs && git fetch origin claude/project-thread-o5rbz8 && git checkout FETCH_HEAD -- pipeline it` (do NOT commit from /root/pkarbs). Paste the commit id and `sha256sum pipeline/forward/late_books.py`.
2. `python3 -m pytest -q pipeline/tests/test_late_books.py` and paste the last line (expect `7 passed`).
3. `mkdir -p /mnt/HC_Volume_107257520/late-books`.
4. `cp it/units/late-books.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now late-books.service` (Restart=always is in the unit).
5. `bash it/late_books_preflight.sh` (paste all of it; every FAIL fixed within 15 min or named), then `bash it/late_books_live_read.sh` (pid line must show a number; file growth is only expected inside a window).
6. Disk: about 1 MB per day; no floor issue.

## HEALTH READ (Nick standing rule R-037: within 15 min of every start or restart)
Run `python3 pipeline/forward/late_books.py health --series-file it/late_books_series.txt --out /mnt/HC_Volume_107257520/late-books --minutes 15` and `pgrep -f 'late_books.py record'`, and post both outputs in reviewer/pkarbs/INBOX.md. PASS needs: pct >= 99 (null = no window fell due in the period, then name the next window), errors 0, own_book_ok true, disk_free_GB shown, a pid. The `price_source` line names the fields: ask, bid and depth02 are the best own ask and bid of the leader token (field `token`) from POST /books, never 1 minus the other token. On any FAIL: stop the service (`systemctl stop late-books.service`), keep the files, fix, restart, post a new read within 15 min, and say in plain English what the failure means (for example: windows missed means those events cannot be used in the depth table).

## Schedule (dated windows: it/SCHEDULE-late-books-2026-11-22.md)
Today the first window is box-office-openings (13 open events) at T-3h Sun 22 Nov 09:00Z and T-1h 11:00Z. If the service is not up by 09:00Z that window is missed and the 11:00Z and 11:30Z windows still count. At least 30 minutes before each listed window run the preflight; 15 minutes after the first window paste the first line of `/mnt/HC_Volume_107257520/late-books/late_books_20261122.jsonl` (plausible = `hours_to_end` within 0.02 of 3.0, `ask` between 0.01 and 0.99, `latency_s` under 5).

## Report in agent/outbox
`systemctl is-enabled`, `systemctl is-active`, pid, the sha256, the preflight output, and each day the number of lines in the day's file and the number of `error` lines in `journalctl -u late-books.service` (expect 0). The pipeline thread runs `python3 pipeline/forward/late_books.py summarize --out /mnt/HC_Volume_107257520/late-books` on the pasted files; send the file copies to `/mnt/project-files/pipeline/forward-data/late-books/` once a day.
