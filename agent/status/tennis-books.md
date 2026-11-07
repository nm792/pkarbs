# status: tennis-books (TASK-tennis-books-2026-11-05)
state: COMPLETED — data route VERIFIED COMPLETE (2026-11-07 05:28Z). No tail gap.
unit: was tennis-books-v2.service (systemd-run transient, MemoryMax 500M); no longer present (transient run ended).
data_route: CHARTER 383/384 — box is the store; nothing raw committed.
  local raw: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05/share/books.jsonl (1,002,747,113 B, 1,048,467 rows, stopped 21:10Z)
  box: pkarbs/tennis-2026-11-05/share/* STORAGE-BOX VERIFIED 2026-11-07 05:26Z:
    share/books.jsonl 1,002,747,113 B @21:10:36Z == local (rsync --checksum dry-run: 0 transfers, checksum-clean, plus tennis_books_2026-11-05.jsonl.gz 166,866,252 B @08:34:49Z)
    share/{log,markets,probe}.jsonl all present matching local.
RESOLUTION: the 23:05Z 5-Nov "tail 18:07Z→21:10Z never shipped / owner decides ship-vs-discard" note is SUPERSEDED — the full final share/ set (through 21:10Z) is ON the box, checksum-verified. Accounts for the earlier 18:07Z partial + later full-file box ship. Nothing to ship, nothing to discard; task data route complete.
next: task closed (no remaining owner decision).
last heartbeat: 2026-11-07T05:28Z UTC
