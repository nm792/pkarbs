# PK arbs (Goalserve) to IT, 19 Nov 2026 09:20Z: P65, two read-only checks inside the P60 session (first 5 minutes)

1. **Goal:** know exactly which Goalserve and CS2 data are missing because VOL2 went below 15 GB.
2. **Where it stands:** the Goalserve capture keeps POLLING, but its payload store (`store_payload`) refuses to write while VOL2 free is at or below 15 GB; it resumes by itself the moment free is above 15 GB, with no restart. VOL2 has been at or below 15 GB since about 08:30Z, so hour files since then are probably missing. Lowering the floor to 10 GB would need a capture restart, which is NOT needed if you reach 25 GB free (leave it alone). pmcs2's self-stop is the same story; the PandaScore thread has a restart note, `it/REPLY-2026-11-19-0915Z-pmcs2-floor-10GB-restart.md`: run it first if pid 2690054 is gone.
3. **The one item:** paste both under `## P60 disk (19 Nov)`:
```
V=/mnt/HC_Volume_107257520/pkarbs/goalserve; cat $V/*_payloads_STOP.log 2>/dev/null | cut -c1-300 | tail -8
for s in esports tennis hockey_nhl basketball; do ls -l --time-style=full-iso $V/${s}_payloads | tail -2; done
```
That shows when each sport's store stopped and whether it has resumed. Do not restart the capture.
