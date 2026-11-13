# agent/status/netflix-chart-recorder-class4.md — INSTALLED (X432 made 9/10/11 Type A); CB9 book-snap TIMEOUT defect
status: INSTALLED 2026-11-11 (X432 reclassified CHANGE-BATCH 9/10/11 Type A); **CB9 netflix book-snap partial fail**
Updated 2026-11-12T05:29:40Z UTC.

**Installed, live:**
- pkarbs-netflix-recorder.timer/service (CB9, 30 min; TimeoutStartSec=600, MemoryMax 300M)
- pkarbs-charts-recorder.timer/service (CB10, 3 h) — healthy, /vol2/pkarbs/charts/ charts_20261112.jsonl.gz fresh (05:27Z)
- pkarbs-mentions-recorder.timer/service (CB11, 5 min) — healthy, /vol2/pkarbs/mentions/ books_20261112.jsonl.gz fresh (05:25Z); 8/8 tests passed per IT-STATUS

**CB9 netflix defect (measured 2026-11-12T05:29:40Z UTC):** the what's-on-netflix daily fetch WORKS (wn_daily.jsonl 899 KB, 110 rows, fresh 05:00Z) but the Polymarket book-snap pass never completes within the 600 s unit timeout (start operation timed out 04:40, 05:10Z; books.jsonl.gz still 0 bytes since 02:13Z 11 Nov). Root cause: snap_books() iterates every open "Netflix this week" event roster + clob /book per market with 0.15 s sleep — too slow for a 600 s window. Net effect: the free daily Netflix signal is captured; the Polymarket book data this logger was installed to record is NOT. Fix (capped, not applied here): bound/sample the book set, raise TimeoutStartSec, or split the book pass — a code/unit change (CHANGE-BATCH / gated). No file/env/unit touched to write this status.
Revert for the install: remove the 3 timers/services.
