# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (Ruling-A restart 2026-11-05T15:10:36Z)
reason: Ruling-disk-gate (05:25Z) gate = root >=6GB free at start; root now 19.2GB free/50% used — GO. Nick 04:43Z "run if clear" + tennis-books-go note.
unit: tennis-books-v2.service (systemd-run, idle:timeout 22800, MemoryMax 500M), pid 554848/554854, started 15:10:36Z.
hard stop: kill scope + keep committed if /root/tennis-books >2GB OR root free <5GB. Both clear.
last commit: 758e7e8e 18:05Z - books.jsonl.part3.gz (93.5MB single part, 15:10-18:05Z run), log/markets/probe .gz refreshed.
raw files: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05/share/books.jsonl (534MB, growing); gzipped parts committed to origin, raw kept locally until next commit-delete.
df at 18:05Z: / 19.2GB free / 50% used (via /dev/sda1).
next: continue hourly gz+commit; delete committed raw after each commit; stop per hard-stop rules.
last heartbeat: 2026-11-05T18:05Z UTC
