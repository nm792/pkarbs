# IT 05:10Z 18 Nov: P22 done; every PK arbs row now waits on the dirty checkout

1. **Goal:** Goalserve odds v2 run as the accepted sequential test (reviewer/REVIEW-RESPONSE-2026-11-18-goalserve-conditions.md, df779ff: design ACCEPTED at 9d4857d4, PREREG V23).
2. **Where it stands:** P22 disk inventory landed at 04:37Z (agent/status/goalserve.md, 8a9310c9). The data volume had 28G free at 04:35Z and 27G at 05:04Z (P23 report 8be9a3ab), so P18's 20 GB gate now passes. The largest consumers are pkarbs/thesports at 40G and pkarbs/scratch at 8.4G. The ship_raw cron line is present and no ship_raw process was running. Nothing was deleted.
3. **Most important item:** the dirty `/root/pkarbs` checkout blocks P18 (E1 smoke), P21 (chunk F), P23 (chunk G) and P16. P23's `git pull -q` was refused at 05:06Z (8be9a3ab): local changes and untracked files would be overwritten. The P16s ruling is still owed (since 17 Nov 16:56Z, 81d3ad3f): 1.98 GB untracked hit the 500 MB stash gate.

Items:
- P22 is closed. P18 and P23 are `waiting:` on your P16s ruling (dialogue bfd83ac1). No PK arbs row is `open`, so the 2-hour floor cannot be met until you rule.
- NEEDS RULING (one of these): (a) stash anyway, including untracked; root has 13G free, so check the stash would fit; (b) stash only the tracked changes and move the named untracked paths to a data-volume folder you name; (c) another exact command list. Once ruled, IT routes it as one chunked row and reopens P18, then P23.
- No deletion list is needed for P18 now, because the disk gate passes. Deletions on the data volume (thesports, scratch) stay your call.
- Minor: the P23 session wrote its WAKE row to pkarbs `status/WAKE.tsv` (8be9a3ab) instead of dialogue `status/WAKE.tsv`. It does no harm and IT will not touch it.
