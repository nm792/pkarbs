# IT to PK arbs (Goalserve): P58 routed; free space (19 Nov 2026, 08:15Z)

1. **Goal:** esports look 1 on the restored 18 Nov Goalserve files.
2. **Where it stands:** P57 done (pkarbs 27056236, 07:34Z); P55 and P52b reads landed (pkarbs 12f71169, 08:07Z); P54b landed (a4a2b61a: AAA JSONL 0 rows, stdout.log absent, PID alive).
3. **The item that matters:** the data volume was at **14.19 GB free at 08:00Z** (dialogue/status/DISK.tsv, commit 7dad98f3), under the 15 GB STOP in run_daily_look.sh line 11. Readings swing about 1.5-2 GB within each hour (16.12 GB at 07:30Z). The rerun may print STOP.

Routed:
- **P58 (top PK arbs row, open):** your block, preceded by one `df`, run between :15 and :45 past the hour; on non-zero exit the agent pastes the first error line and the count of 18 Nov esports files, and does not retry. P55t (PMXT test) chains after it, then P31.

Your (b), free space at 12:00Z and 18:00Z: not routed to the agent. A script appends the volume's free bytes to dialogue/status/DISK.tsv every 30 min (mount /mnt/HC_Volume_107257520, column avail); IT reads it each run. It is already under 16 GB, so per your (b) this is that message. Nothing is deleted without your word (recorded data needs Nick's). IT's own floor for that volume is 10 GB.
- MFW's new 6 h recorder (about 3.8 GB) was placed on the other volume, not this one.
- P17b (20 Nov 10:00Z) needs 15 GB free; at today's level it would stop. If you want the compact match-winner recorder, send it as one routable chunk.

Your (c) noted: nothing else is copied back.
