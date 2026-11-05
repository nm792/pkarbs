# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (started 2026-11-05T05:32:24Z)
owner ruling: agent/outbox/question-2026-11-05-tennis-oddspapi-disk-gate.md (05:25Z) — gate now root >= 6 GB free (was 10 GB/75%).
disk: / 7.85 GB free (05:31Z) >= 6 GB. RUNNING.
run: capture.py /root/tennis-books/2026-11-05 12 --share .../share (pid 2705528, timeout 43500, MemoryMax 500M), tracked bg.
progress 05:33Z: books.jsonl 878 KB growing, markets.jsonl 74 tokens, probe.jsonl writing.
hourly: gzip+commit share/*.jsonl -> rn1/scores/tennis/books-2026-11-05/ on default branch; delete committed raw after.
HARD STOP: kill scope + keep committed if /root/tennis-books > 2 GB OR root free < 5 GB (write stop in this status).
pass/fail per task: books.jsonl grows, markets.jsonl >=20 distinct tennis events, probe.jsonl >=10 clob_rtt rows.
revert: kill scope, rm -rf /root/tennis-books. Key never committed.
last heartbeat: 2026-11-05T05:33Z UTC
