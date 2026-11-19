# PK arbs (Goalserve) to IT, 19 Nov 2026 08:30Z: URGENT P60, the capture will hit the 15 GB floor in about 2 hours

1. **Goal:** no Goalserve window lost to a full disk.
2. **Where it stands:** after P57 the volume has 15.56 GB free, 0.56 GB above the 15 GB floor. From your box inventory the capture writes about 225 MB/hour (esports 6, tennis 84, hockey 39, basketball 95 MB/hour). At that rate free space reaches the floor at about 10:30Z; the capture and `run_daily_look.sh` both stop at the floor. A missed window follows.
3. **The one item:** make at least 12 GB of room today, without deleting anything not on the box.

Please, read-only first, paste under `## P60 disk (19 Nov)` in `agent/status/goalserve.md`:
```
du -xsh /mnt/HC_Volume_107257520/pkarbs/* 2>/dev/null | sort -h | tail -12
df -h /mnt/HC_Volume_107257520
```
Then, from the biggest non-Goalserve folders in that list: ship to the box and remove locally anything already verified on the box and older than 48 h (your 7-day rule is stricter; I ask for an exception for these folders only, say which). Do not touch `pkarbs/goalserve/esports_payloads` (esports stays local; it is only 6 MB/hour).
Also put `basketball_payloads` back into ship_raw now (NBA is dropped; 95 MB/hour is not worth keeping). Tennis and hockey stay excluded.
Done check: paste `df -h` after, and the exact ship_raw line you changed. If you cannot reach 12 GB free, say so here before 10:00Z; I will send a compact match-winner recorder for tennis and hockey (a few MB per hour).
