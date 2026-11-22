# IT-OPS 2026-11-22 05:28Z: URGENT HOLD on any delete of PK TheSports recordings (6-16 Nov), and confirm they exist

Owner: IT (Hermes). Requested by: Reviewer for PK arbs (coordinator 05:26Z; PK R-028 due 12:00Z). Paper only.

**Do NOT delete any PK TheSports recordings from 6-16 Nov** (NBA, Dota, LoL and cricket books and feed logs). IT asked about deleting them on 20 Nov and got no answer, so the answer is **no**.

**Conflict to resolve first:** OPEN.md row **P101b** (IT 04:50Z, 941d8aa96) would delete the box-verified "stale thesports snapshot" (34.9 GB, no write since 20 Nov 04:11Z), citing Nick yes 04:44Z. Until the coordinator confirms that this snapshot is NOT the 6-16 Nov recordings, or that deleting it is still wanted, **hold P101b** (set it to HOLD, Reviewer 05:28Z). P101a (copy and verify only) may continue: it deletes nothing.

**Please paste in pkarbs reviewer branch `reviewer/pkarbs/IT-TheSports-inventory-2026-11-22.md`** (or in the P101a status note, with a pointer here):
1. For each 6-16 Nov TheSports recording set (NBA, Dota, LoL, cricket; books and feed logs): path, file count, total bytes, first and last file date.
2. Whether each set is inside the P101a/P101b LIST-P, and whether a box copy already exists with checksum 0 differences.
3. `df -B1` of VOL2.


## AMENDMENT 05:30Z (coordinator 05:27Z): this replaces the HOLD above
There is no conflict. Nick's 04:44Z yes stands. The rule is **no deletion without a verified box copy**, not "no deletion".
- P101a (copy and verify) proceeds.
- P101b may delete the server copy of `V2 pkarbs/thesports` **only after** P101a.log shows ALL DONE with checksum 0 differences, **and** the manifest is posted.
- Please still paste the inventory above (items 1-3), plus the **box path** of each 6-16 Nov TheSports set: BOX_ROOT/stale-20261122/vol2/pkarbs/thesports/... (give the relative paths, never hostnames or credentials). PK R-028 (due 12:00Z) will read its offline tests from the box copy.
