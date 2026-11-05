# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (started 2026-11-05T05:32:24Z)
owner ruling: root >= 6 GB free gate (05:25Z). current root free 5.89 GB, /root/tennis-books 776M (well under 2 GB hard stop).
run: capture.py /root/tennis-books/2026-11-05 12 --share (pid 2705541 alive 10:33Z, timeout 43500, MemoryMax 500M), tracked bg.
hourly: gzip+commit share/* -> rn1/scores/tennis/books-2026-11-05/. LAST hourly 08:02Z (commit 3e2217b); 09:0XZ was only a snapshot (e46a270) not a gzip+commit. OVERDUE caught 10:33Z: gzipped books 395MB raw->46.9MB + probe/markets/log, committed 8c7a3b7f on claude/project-thread-vg2ckg. Raw books.jsonl kept (capture appends to it; delete at end per ruling).
progress: probe.jsonl clob_rtt rtt_ms 50.2 writing.
HARD STOP: >2 GB OR root free <5 GB (write stop here).
last heartbeat: 2026-11-05T10:33Z UTC
