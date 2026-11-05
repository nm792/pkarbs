# status: tennis-books (TASK-tennis-books-2026-11-05)
state: RUNNING (Ruling-A restart 2026-11-05T15:10:36Z)
reason: Ruling-disk-gate (05:25Z) gate = root >=6GB free at start; root 19.2GB free/50% used — GO. Nick 04:43Z "run if clear" + tennis-books-go note.
unit: tennis-books-v2.service (systemd-run, MemoryMax 500M), pid 554848/554854, started 15:10:36Z.
hard stop: kill scope + keep committed if /root/tennis-books >2GB OR root free <5GB. Both clear (19.2GB free).
DATA ROUTE (CHARTER 383 pre-push hook, installed 14:08Z): raw/.gz >5MB or .gz/.jsonl >1MB CANNOT push to git outside manifest/. part1/part2 on origin predate the hook. Current run data SHIPPED TO STORAGE BOX instead (per 384 release: tennis -> /vol2 + hourly box ship + nothing raw committed):
  box: pkarbs/tennis-2026-11-05/ books.part3.gz(93.5MB) log/markets/probe.jsonl.gz  @ 18:07Z, checksum-verified.
local raw: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05/share/books.jsonl (534MB, growing); gz'd to box hourly.
correction: earlier 18:05Z heartbeat/status claimed part3 "committed to git (758e7e8e/fab6e)" — REJECTED by pre-push hook; retracted here. No git commit occurred.
df at 18:05Z: / 19.2GB free / 50% used.
next: box ship hourly; delete-committed-raw rule is now box-verified route; stop per hard-stop rules.
last heartbeat: 2026-11-05T18:10Z UTC
