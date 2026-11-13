# Reply: capture write path (13 Nov 16:36Z) - ruling requested, nothing moved

Answers `agent/inbox/TO-IT-URGENT-move-captures-off-root-disk-2026-11-13.md`. Measured
this session; no path, process or guard was changed by this reply.

- **The finding is confirmed:** `/vol2` is a plain directory on the root volume
  (`findmnt -T /vol2` -> the root device), so the Goalserve payload store, the PandaScore
  capture and the TheSports writers.conf row all write to root, against charter clause 2.
- **The ruling this note asks for is already in the approval queue:** `dialogue/APPROVALS.md`
  **#20** (repoint `PAYDIR` and the PandaScore `OUT` to the data volume, move, restart,
  delete the root copies only after row counts match) and **#21** (gamma `limit` cap, the
  reason registration is frozen). Both are class 4 and are on the daily approval batch;
  this session applied neither.
- **Measured headroom:** root free 17,470,000,000 B at 16:2xZ (55% used), above the
  15 GB floor; the payload store writes ~279 MB/day gzipped (measured 15:09-15:17Z) and
  self-stops at the floor (`esports_payloads_STOP.log`). So waiting for the daily approval
  costs nothing today; the auto-stop is the safety net.
- **Nothing was moved, so no row counts changed and no restart gap exists.** Revert
  path: none needed (no state change).
- **Guards:** the disk-floor check still reads `/` for these writers, which is correct
  for the current layout; it must be repointed in the same change as #20, not separately.

One line to IT: rule (a), (b) or (c) from this note at the next approval batch - #20
already carries the exact command and revert.
