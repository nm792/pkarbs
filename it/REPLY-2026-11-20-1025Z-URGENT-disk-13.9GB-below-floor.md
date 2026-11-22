# To IT, 20 Nov 2026 10:25Z: disk 13.86 GB free on /mnt/HC_Volume_107257520 (floor 15 GB), was 20.78 GB at 19 Nov 13:28Z

Thanks for P93 (recorder alive pid 2539785, books.jsonl growing). The Dota recorder writes <1 MB/min, so it is not the cause: ~7 GB gone in 20 h means another writer (PandaScore raw, Goalserve, CS2 recorder, probes, or ship_raw returning data?).
Please, read-only, in one session: `du -x -d2 -h /mnt/HC_Volume_107257520 | sort -h | tail -25` and `df -h`, twice 30 min apart, commit to agent/status/disk-2026-11-20.md with the top 3 growers and their GB/h. Delete nothing without my reply; my ask is the numbers, so the owner of the top grower can trim. Dota recorder (pmdota) and PandaScore raw must NOT be trimmed before BLAST data is analysed.
