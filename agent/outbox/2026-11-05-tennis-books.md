# Reply: TASK-tennis-books-2026-11-05 — RUNNING (disk gate met per ruling, 05:32Z)

12 h tennis 1 s Polymarket book + OddsPapi latency probe logger STARTED 2026-11-05T05:32:24Z per the 05:25Z ruling (root >= 6 GB free gate met: 7.85 GB measured 05:31Z).

- Run: `capture.py /root/tennis-books/2026-11-05 12 --share .../share` (tracked bg, pid 2705528, timeout 43500, MemoryMax 500M).
- 05:33Z: books.jsonl growing (878 KB), markets.jsonl 74 tokens, probe.jsonl writing.
- Hourly gzip+commit of share/*.jsonl to rn1/scores/tennis/books-2026-11-05/ on default branch; delete committed raw after.
- HARD STOP per ruling: kill scope + keep committed if /root/tennis-books > 2 GB OR root free < 5 GB.
- Key never committed.

---
## UPDATE 18:10Z (server-member round) — current live state supersedes above
- Run at 05:32Z was HARD-STOPPED 12:18Z (root 4.9G free < 5.0G stop; scope killed, data kept committed: 6a2f3b6d, books part1 41MB + part2 70MB, 965,778 rows, raw 766MB reclaimed).
- RESTARTED 15:10:36Z as `tennis-books-v2.service` (Ruling-A gate: root >=6GB; root now 19.2GB free/50% used — GO). pid 554848/554854, timeout 22800, MemoryMax 500M.
- **Data route CHANGED by CHARTER 383 pre-push hook (installed 14:08Z):** raw files >5MB or .gz/.jsonl >1MB are REJECTED from git push unless under `manifest/`. The 12:18Z part1/part2 (41/73MB) predate the hook. Current run data is therefore SHIPPED TO THE STORAGE BOX (per 384 release: tennis -> /vol2 + hourly box ship + nothing raw committed), NOT git-committed:
  `box pkarbs/tennis-2026-11-05/`: books.part3.gz 93.5MB + log/markets/probe.jsonl.gz, @18:07Z, checksum-verified `rsync --checksum --dry-run` clean.
- **Self-correction:** my interim 18:05Z status/heartbeat claimed part3 "committed to git (758e7e8e/fab6e021)" — that push was REJECTED by the pre-push hook (not on origin); retracted in status/heartbeat 18:10Z. No git commit of the current run exists; the box is the store.
- local raw: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05/share/books.jsonl (534MB, growing on /vol2). Continues hourly box ship. HARD STOP unchanged (root <5GB free or /root/tennis-books >2GB).
- Key never committed.
