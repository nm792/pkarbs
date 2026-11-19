# TASK (URGENT, deploy only): run the open-contract book recorder, continuously, starting today

Deploy committed code by SHA and run the stated command. Do not edit the code. Read-only, no keys, no orders.
1. Check out `weekend-perps/open-contracts-2026-11-19/book_recorder.py` at the SHA named in the commit that merges this note (print `git rev-parse HEAD:weekend-perps/open-contracts-2026-11-19/book_recorder.py` and the file SHA-256 in your report).
2. Run `python3 weekend-perps/open-contracts-2026-11-19/test_book_recorder.py` first and paste its last line (expect `RECORDER TESTS PASS`).
3. Install as a PERSISTENT service (not systemd-run): copy `agent/units/oc-book-recorder.service` to /etc/systemd/system, set REPO_PATH, `systemctl daemon-reload && systemctl enable --now oc-book-recorder.service`. Output goes to /mnt/HC_Volume_107257520/ocbooks (about 20 MB/day; keep the 15 GB root floor).
4. Report in agent/outbox: `systemctl is-enabled`, first/last timestamps, rows per minute (expect about 24 lines per 10 s poll when 2 events x 2 tokens x several open dates are active), and the number of `err` lines (expect 0).
5. Keep it running through every trading day; the open is 09:30 New York time, the recorder stops by itself 5 minutes after each open.
Deadline for steps 1-4: 19 Nov 06:00Z (the 19 Nov open is 14:30Z, so the 19 Nov book is the first one we can capture in full).
