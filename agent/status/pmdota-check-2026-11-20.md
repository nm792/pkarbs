P93 — PK arbs Dota recorder live read (2026-11-20)

Read-only check at 09:42:48Z, before the first BLAST window scheduled for 11:00Z. No restart or other change.

Required code revision: `8378b14cb0` is an ancestor of the fetched default-branch tip. The checker was not present in the stale local checkout, so it was read from that origin tip and run from VOL2 scratch.

Checker output:
```text
now 2026-11-20T09:42:48Z
PASS process pid 2539785 started Thu Nov 19 01:13:04 2026
total book rows (gz + current): 129687
newest book row age_s 50
conds with both tokens in current books.jsonl:
3 conds, 3 with both tokens
recorder.log: gamma status lines 0, book errors 0, discover errors 0
2026-11-19T22:23:48.492Z market Dota 2: Inner Circle vs CyberHero (BO5) - DreamLeague Division 2 Playoffs
2026-11-19T23:43:51.351Z market Dota 2: potn9ki vs Team Synapse - Game 1 Winner
2026-11-19T23:43:51.352Z market Dota 2: potn9ki vs Team Synapse - Game 2 Winner
2026-11-19T23:43:51.352Z market Dota 2: potn9ki vs Team Synapse (BO3) - European Pro League Group B
avail GB 13.86
```

Two directory snapshots 60 seconds apart: `books.jsonl` grew from 7,705 bytes at 09:41:58Z to 11,016 bytes at 09:43:40Z. The other listed files did not change. No configured BLAST 11:00Z game was in its scheduled window at either snapshot. The current book file was nevertheless being written; this check does not establish that those rows belong to the BLAST markets.

`df -h /mnt/HC_Volume_107257520`: 98G total, 80G used, 13G available, 87% used. No restart performed.
