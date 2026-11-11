# status: tennis-books (TASK-tennis-books-2026-11-05)
state: COMPLETED at timeout (~21:30Z). Ruling-A restart 2026-11-05T15:10:36Z ran to its 22800s timeout; books.jsonl stopped 21:10Z.
unit: was tennis-books-v2.service (systemd-run transient, MemoryMax 500M); no longer present (transient run ended).
disk_gate (note 385 §1.4, 23:05Z): `pkarbs 500/day -> /mnt/HC_Volume_107257520/pkarbs/tennis` on VOL2 → GO (free 26G, cap 20480MB, use 0, headroom 20480MB). No reference to the superseded 05:25Z root>=6GB ruling — the gate is now disk_gate.sh.
DATA ROUTE (CHARTER 383 pre-push hook): raw/.gz >5MB cannot push to git; run data shipped to STORAGE BOX (tennis -> /vol2 + hourly box ship + nothing raw committed):
  local raw: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05/share/books.jsonl (1,048,467 rows, 1.0GB) — final, stopped 21:10Z.
  box: pkarbs/tennis-2026-11-05/ holds ONLY books.part3.gz(93.5MB)+log/markets/probe.jsonl.gz @18:07Z.
GAP: 18:07Z→21:10Z tail (last ~3h of the run) was never shipped to the box — no hourly box ship covered it after 18:07Z. Box ship of the tail or explicit discard is an owner/reviewer decision; not silently done.
next: owner decides ship-vs-discard of the tail; else task closed.
last heartbeat: 2026-11-05T23:05Z UTC (corrected from stale RUNNING snapshot 18:10Z)
