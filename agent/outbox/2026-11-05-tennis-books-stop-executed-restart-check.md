# outbox/2026-11-05-tennis-books-stop-executed-restart-check

From the pkarbs agent, 2026-11-05 ~12:35Z. Reading back to the reviewer on ruling-disk-gate-2026-11-05 (05:25Z).

## Confirmation the hard-stop was executed per the ruling
- **Condition hit:** root fell to 4.7 GB free — the ruling's hard-stop triggers on `root free < 5 GB`. Stopped at 12:18Z.
- **Kept what was committed:** tennis-books captured ~03:00Z–12:18Z; committed to `rn1/scores/tennis/books-2026-11-05/` — part1 41.2 MB + part2 73.1 MB (965,778 rows) + the earlier hourly books.jsonl.gz 46.9 MB, plus log/markets/probe. All `gzip -t` OK. Status written to `agent/status/tennis-books.md` (STOPPED 12:18Z, reason/disk, revert).
- **Deleted committed raw:** `/root/tennis-books/2026-11-05` raw cleared per the ruling's delete-the-committed rule; reclaimed ~1.5 GB → **root now 5.9 GB free / 84%**.
- **No respawn guard:** confirmed none (cron/tmux) — it will not restart itself.

## Restart decision requested (per the ruling's own start gate)
- The ruling's start condition: **root >= 6 GB free.** Root is 5.9 GB now — just under.
- cricket-feeds is still running (separately approved, untouched) and keeps consuming root.
- **Ask:** should tennis-books relaunch (a) automatically when root clears 6 GB, (b) only on a fresh reviewer note clearing disk, or (c) stay stopped for today given the capture is already 965k rows? The launch/stop conditions in ruling-disk-gate-2026-11-05 remain otherwise unchanged from our side.
- Note: this is an outbox reply; no code change, no process touched in writing it. Tennis-books is left stopped (no restart without this ruling or Nick overriding directly per the ruling's last line).
