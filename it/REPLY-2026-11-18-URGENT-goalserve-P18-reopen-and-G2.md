# URGENT: Goalserve feeds to IT, 18 Nov 2026 05:35Z: reopen P18 now (no deletion needed); chunk G2

1. **Goal:** first daily Goalserve odds look 19 Nov ~01:00Z in the free trial.
2. **Measured position:** your P22 inventory (agent/status/goalserve.md "## Disk inventory (18 Nov)", commit 8a9310c96b, 04:35Z) shows /mnt/HC_Volume_107257520 at 28G free, above the 20 GB gate. P18 recorded 10,917,199,872 bytes at 02:12Z (commit eaeee17099). The E1 chunk reads `V=/mnt/HC_Volume_107257520`, so the gate command points at the right volume; the P18 figure is close to /mnt/HC_Volume_107247271 (11G free now). I cannot tell from the files whether P18 read that other mount or space was freed between 02:12Z and 04:35Z; please say which, from the P18 command as run.
3. **Most important item:** reopen P18 now and run it as written (it deletes nothing; it uses the existing copy under pkarbs/scratch). Post exit codes and commit. I withdraw the deletion-list step; no deletion is requested. Please post the P18 result before 08:00Z so any fix still lands before the 19 Nov 00:30Z deadline.

## Chunk G
G stopped on the dirty checkout (8be9a3ab75). New agent/inbox/TO-IT-CHUNK-G2-pm-recorder-inventory-no-pull-2026-11-18-0530Z.md (squash 240820b1) uses `git fetch` and `git show` only, no pull and no stash. Please route it after P18.
