# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (started 2026-11-05T05:32:24Z)
owner ruling: root >= 6 GB free gate (05:25Z moved to >=6GB, hard stop: /root/tennis-books >2GB OR root free <5GB).
run: capture.py /root/tennis-books/2026-11-05 12 --share (pid live, timeout 43500, MemoryMax 500M), tracked bg.
hourly: gzip+commit share/* -> rn1/scores/tennis/books-2026-11-05/. LAST committed 10:33Z (8c7a3b7f, books 395MB raw -> 46.9MB gz). Next ~11:45Z.
sizes (11:45Z): /root/tennis-books 1.4G (raw capture appends; delete-after-commit per ruling). root free 5.19G (87% used) - CLOSE to 5GB hard stop but still above; watching each hour.
progress: probe.jsonl clob_rtt still writing.
HARD STOP: kill scope + keep committed if /root/tennis-books >2GB OR root free <5GB (write stop here).
last heartbeat: 2026-11-05T11:45Z UTC
