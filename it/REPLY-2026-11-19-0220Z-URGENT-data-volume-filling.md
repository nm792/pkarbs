# To IT, 19 Nov 2026 02:20Z: URGENT, what is filling the data volume (about 0.8 GB/h), answer by 03:15Z

1. **Goal.** Keep every feed recorder (Dota both-token books, PandaScore, Goalserve) writing through BLAST Slam IX (20-29 Nov) without stopping on the 15 GB floor.
2. **Where it stands.** Free space on /mnt/HC_Volume_107257520: 20,746,121,216 B at 18 Nov 22:44:21Z, 18,323,320,832 B at 19 Nov 01:47:37Z (pm-dota-books-2026-11-18.md, dc638fadf6). That is -2.42 GB in 3 h 03 min = about 0.79 GB/h. At that rate the 15 GB floor is reached at about 06:00Z today. The Dota recorder (P40, PID 2539785) writes at most about 0.05 GB/h and its books file is empty until 09:40Z, so it is not the cause.
3. **One item.** Read-only, one reply: `du -sb` for each top-level directory under `/mnt/HC_Volume_107257520/pkarbs/` (and `scratch/` subdirectories), twice 10 minutes apart, and say which one grew most. Name the job that writes it. Then say what trims it before 05:00Z (gzip, move to the storage box, delete a named scratch copy) and what it frees in GB. Do not delete recorded data without Nick's word; scratch copies of inputs (for example `scratch/goalserve-run-tree`, `p318-recount`) are the first candidates, named explicitly.
If it cannot be trimmed, say when each recorder will stop and in what order.

Confidence 8/10: two readings 3 h apart; the cause is IT's to find.
