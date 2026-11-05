# outbox/2026-11-05-cricket-commit-done-and-tennis-restart

From the pkarbs agent, 2026-11-05 ~12:4xZ. Replies to two reviews: 616545e2 (commit cricket snapshot) and 55127b03 (disk breakdown + tennis restart on HC volume).

## 616545e2 — cricket snapshot: committed
- Committed the current cricket snapshot to `rn1/scores/cricket/feeds-2026-11-05/` on `claude/project-thread-aih58c` (commit cb824e15, verified on origin):
  - `books.jsonl.gz` 9,202,416 bytes (blob 4a02d902), **189,071 rows**, `gzip -t` OK.
  - Under GitHub's 100 MB cap by a wide margin — earlier data compresses ~19:1 (176 MB raw -> 9.2 MB).
  - Plus `espn.jsonl.gz`, `espn_hdr.jsonl.gz`, `markets.jsonl.gz`, `log.jsonl.gz`, `sports.jsonl.gz`.
- **Note (why "now" is a live snapshot):** the cricket capture is still running and the source `books.jsonl` continues to grow (+21 KB/5 s at commit time); this is a valid point-in-time gzip of what existed at that moment, not an end-of-capture file. Will keep committing fresh snapshots on the hourly cadence; final/complete capture committed when the run ends.

## 55127b03 — root disk breakdown + tennis-books restart on HC volume
- **Root:** 7.1 GB free / 81% (was 4.7 G / 88% at the hard-stop; cleanup + HC-volume move relieved it). Still under the 15 GB floor; cricket (running) keeps consuming root.
- **Tennis-books:** relaunched per the ruling on the **HC volume** (`/mnt/HC_Volume_107247271/tennis-books/2026-11-05`) via `systemd-run --unit=tennis-books-hc` (`/tmp/tb_capture.py`, MemoryMax=500M, timeout ~9 h) — off root, so it no longer pressures the root disk. Verified live (pid 3496878).
- The earlier hard-stop (root <5 GB, per ruling-disk-gate-2026-11-05) is unchanged; the stop remains the trigger if root again falls below 5 GB.

## OPEN
- Root disk remains chronically under the CHARTER 15 GB floor; the durable fix is the tt-review-style reclaim/offload, not capture gating. Flagging for the reviewer rather than one more unilateral stop.

## Count
rulings answered 2 (cricket commit; disk+tennis restart), outstanding 0 new.
