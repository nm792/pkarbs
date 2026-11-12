# Status: TheSports hand export in progress (inbox thesports-export-by-hand-now-2026-11-11b, 20:50Z)

**Status: STARTED, not yet pushed.**

The CB15-fixed exporter (`export_timer_2h.sh`, de0517c84 fix) was launched for this inbox on 11 Nov 21:04Z and is mid-run right now. Measured at 23:40Z:

- Boundary (SINCE): newest committed ts_mqtt minute = 1794384103 (08:01Z) — exporter starts from the committed tip, correct.
- Files built: manifest reports TOTAL_FILES 43670; stage `/mnt/HC_Volume_107257520/pkarbs/scratch/ts_slim_stage` = 258M and growing (still indexing new ts_mqtt chunks).
- Process: pid 3608478 alive, actively running git `update-index --add --cacheinfo` on the new chunk set (a fresh indexing child was live at this check).
- Origin newest ts_mqtt chunk as of 23:35Z: still `1794384000000/` (10:00Z). Nothing pushed yet — the exporter fetches the fresh origin tip only AFTER the slow export/index finishes, which is the CB15 fix, so the push lands in ms once the index completes.

Nothing is stranded: the run is single-instanced (flock `thesports-slim.lock`), self-managed, and will push the built chunk set as one fast-forward commit on this branch when the index finishes. I am not starting a second instance (that would race the boundary and the lock).

I will append the pushed commit hash + an origin-side "newest ts_mqtt > 1794384000000" verification when this run lands.
