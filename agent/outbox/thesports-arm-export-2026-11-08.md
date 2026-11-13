# thesports-arm-export reply — 2026-11-08T02:20Z

**1. Capture verified live.** `final-topics-32295b` is being written by `thesports-capture-b` (systemd-run scope, pid active, single instance). Live file mtimes advance to 02:16Z; row counts (share .gz snapshot @02:09Z): ts_mqtt 80,948 · books 122,707 · pmws 1,195 · markets 358 · ts_poll 70 · log 51. No second instance (one pid tree).

**2. First 2h slim export committed.** Built `rn1/scores/thesports/final-topics-32295b-slim/` (same per-hour ts_mqtt + per-15min books_mid + counts.json layout as `final-topics-32295-slim`): 101 ts_mqtt parts, 89,525 ts_mqtt rows, 121,938 books_mid rows, covering 00:39Z→02:09Z. Pushed as `1968b201`. Recurring 2h cadence rides the existing dispatcher (same scripts/pattern as the prior 32295 slim); no new cron was needed.

**3. 13:15–14:00Z old-chunk stretch — books gap found and filled.** ts_mqtt 13:15–14:00Z is already covered (committed `final-topics-32295-slim/ts_mqtt/1794056400000/`, 60 min files). Books were NOT covered: `slim-1102-32295` 13:00Z hour file ends 13:04:58Z, and `final-topics-32295-slim/books_mid/` has no 13:00Z hour (starts 14:00Z). Committed the 13:15:00–13:59:59Z books (116,002 rows, 3 bucket files) into `final-topics-32295-slim/books_mid/1794056400000/`.

**NOTE:** the strictly 13:15–14:00Z books bucket puts 13:00:00–13:15:00Z (books) still uncovered — that sub-window was not in this note's range; say if it is wanted.
