# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (started 2026-11-05T05:32:24Z)
owner ruling: root >= 6 GB free gate (05:25Z). current root free 6 GB, /root/tennis-books 429M (well under 2 GB hard stop).
run: capture.py /root/tennis-books/2026-11-05 12 --share (pid alive, timeout 43500, MemoryMax 500M), tracked bg.
hourly: gzip+commit share/* -> rn1/scores/tennis/books-2026-11-05/. THIS round (09:0XZ) committed fresh snapshot books.jsonl.gz 17MB + markets/probe/log to origin (commit e46a270, branch claude/project-thread-vg2ckg).
progress: probe.jsonl clob_rtt rtt_ms 50.2 writing.
HARD STOP: >2 GB OR root free <5 GB (write stop here).
last heartbeat: 2026-11-05T09:0XZ UTC
