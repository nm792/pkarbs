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


## P96 live read (20 Nov 15:15Z)

The project checker was extracted from the fetched project tip to VOL2 scratch and passed `bash -n`. Result: PASS process PID 2539785; 217,155 total book rows; newest row age 1 second; 13 conditions with both tokens; recorder log reported 0 gamma status lines, 0 book errors and 0 discover errors. `markets.jsonl` contained 16 BLAST matches. The two requested team-name patterns had 0 matches in current `books.jsonl`. Current book file was 1,965,518 bytes at 15:16:05Z. No restart or data change.


## P96 live read (20 Nov 17:42Z)

Read-only check using `feeds/check_pmdota.sh` from fetched project tip `8378b14cb0fe4579ee53c2d8159e8dacc33b31a9` (checker syntax passed with `bash -n`; executed from VOL2 scratch because the stale checkout did not contain that path). No restart or data change.

Output: PASS recorder PID 2539785, started Thu Nov 19 01:13:04 2026; 260,536 total book rows across hourly gzip files and current file; newest row age 0 seconds; 12 conditions, all 12 with both tokens; 0 gamma status lines, 0 book errors, 0 discover errors. The latest four market lines were timestamped 16:54:22Z. The requested `grep -c BLAST` count was 20; the requested team-name pattern count was 0 in current `books.jsonl` (grep exit 1 means no matches). VOL2 had 10.70 GB available during the check. No restart performed.
