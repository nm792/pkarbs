# URGENT P60 (PK arbs, 19 Nov 2026, 09:05Z): data disk under the 15 GB floor. Do this FIRST, one paste-in block, read the whole page

1. **Goal:** recorders do not stop at the 15 GB floor; at least 12 GB free by 10:00Z.
2. **Where it stands:** your reads: 15.24 GB (08:40Z), 14.33 GB (08:47Z), 14.04 GB (report time). Below 15 GB the Goalserve capture, the CS2 book recorder (pmcs2) and run_daily_look.sh stop themselves. Falling about 3.6 GB/hour: more than the capture alone, so another writer is large. This block finds it.
3. **The one item:** run the block, paste the whole output under `## P60 disk (19 Nov)` in `agent/status/goalserve.md`.
```
V=/mnt/HC_Volume_107257520; date -u +%FT%TZ; df -B1 $V | tail -1
du -xsh $V/pkarbs/* 2>/dev/null | sort -h | tail -12
du -xsh $V/pkarbs/goalserve/* $V/pkarbs/scratch/* 2>/dev/null | sort -h | tail -8
ps -p 4045212 -o pid,etime,cmd | cut -c1-100; tmux ls 2>&1 | head -5
ls -l --time-style=full-iso $V/pkarbs/goalserve/tennis_payloads | tail -2
ls -l --time-style=full-iso $V/pkarbs/pmcs2 2>/dev/null | tail -3; du -sb $V/pkarbs/pmcs2/books.jsonl
```
Then, in this order, stopping when df shows at least 17 GB free:
(a) `$V/pkarbs/scratch/goalserve-run-tree` and `$V/pkarbs/scratch/goalserve-daily-*/gs` are rebuildable copies (the look copies the hour files again each run): remove the `gs` folders only (`rm -rf $V/pkarbs/scratch/goalserve-daily-*/gs`). Keep result-*.json and the other files.
(b) Ship to the box and remove locally anything already verified on the box and older than 48 h, from the biggest folders in the du list that are NOT `pkarbs/goalserve/{esports,tennis,hockey_nhl}_payloads` (exception to the 7-day rule, say which folders). `basketball_payloads` goes back into ship_raw (3 h).
(c) Run P61 (`it/REPLY-2026-11-19-0900Z-...P61...`): compacts finished tennis/hockey hour files in place, verified.
Then paste `df -B1 $V | tail -1`.

## If a recorder has already stopped itself
Tell me here which (capture pid 4045212 gone, or pmcs2 not growing). Restart each exactly as before (capture: tmux session `goalserve`, `live/goalserve/capture.py`; pmcs2: its own start line from agent/status/pandascore.md) ONLY after df shows at least 17 GB free, and paste the restart time. Do not restart while below 15 GB; it stops again at once.
