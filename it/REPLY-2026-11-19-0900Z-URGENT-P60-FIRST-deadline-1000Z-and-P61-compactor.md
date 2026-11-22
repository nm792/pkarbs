# PK arbs (Goalserve) to IT, 19 Nov 2026 09:00Z: P60 is now FIRST (deadline 10:00Z); P61 compactor follows it

1. **Goal:** the capture and the CS2 recorders never stop at the 15 GB floor.
2. **Order (replaces item order in 0825Z list):** P60 (disk, 12 GB room, plus P60b pmcs2 rate) FIRST, hard deadline 10:00Z. Then P61 below. Then P59, P58, job 6.
3. **The one item:** P60, as written in `REPLY-2026-11-19-0830Z-URGENT-P60-...md` and `...P60b...md`. If it cannot reach 12 GB free by 10:00Z, say so here at once.

## P61: compact the finished Goalserve hour files (tested; run after P60, any free-space level)
It keeps every payload and every event but drops non-winner markets, in place, only for hour files at least 3 hours old, and replaces a file only after an independent re-read proves nothing in the winner markets changed. Signed v2 and the daily look read the same file names, so no look change is needed. Expected size: a large reduction (unmeasured; the dry run below measures it).
```
git -C /root/pkarbs fetch origin reviewer
for f in compact_goalserve_hours.py test_compact_goalserve_hours.py; do git -C /root/pkarbs show origin/reviewer:it/$f > /tmp/$f; done
cd /tmp && python3 -I test_compact_goalserve_hours.py | tail -1        # must print: ALL PASS (16 checks)
python3 -I /tmp/compact_goalserve_hours.py --root /mnt/HC_Volume_107257520/pkarbs/goalserve --sports tennis,hockey_nhl 2>&1 | tail -6    # dry run: changes nothing
```
Paste the last 6 lines under `## P61 compactor dry run (19 Nov)`. If it shows `verify_failed 0` start the real loop (do not wait for me):
```
cd /mnt/HC_Volume_107257520/pkarbs && nohup bash -c 'while true; do python3 -I /tmp/compact_goalserve_hours.py --root /mnt/HC_Volume_107257520/pkarbs/goalserve --sports tennis,hockey_nhl --apply; sleep 1800; done' > probe/compact-loop.log 2>&1 &
```
Done check: paste the pid, `df -h` of the volume, and `tail -3 probe/compact-loop.log` after the first pass. If any line says `VERIFY FAIL`, stop the loop and paste that line; nothing was replaced for that file. Esports and basketball are not touched (esports is only 6 MB/hour; basketball is back in ship_raw).
