# P101a — PK arbs stale thesports snapshot to the box

- Result: copy and checksum verification completed. The existing `/mnt/HC_Volume_107257520/ship/P101a.log` records source size 34,906,107,252 bytes, 10 files, `transfer_exit=0` at 06:17:29Z, and `checksum_exit=0 differing=0` at 06:21:17Z, followed by `ALL DONE`.
- Read-back: the box destination `stale-20261122/vol2/pkarbs/thesports/` lists the `final-topics-32295b` data tree and its 10 files. No data was added to git.
- Follow-on state observed at 07:24Z: the local source directory was absent; it existed at 07:20:47Z. The P101a copy log is unchanged, and no `P101b.log` was present. The disappearance is consistent with a subsequent deletion but does not prove its actor, gate checks, or before/after disk readings; this report does not claim P101b verified.
- Revert is not applicable to the completed copy. The local source was not deliberately deleted by this P101a run.

Evidence paths: `/mnt/HC_Volume_107257520/ship/P101a.log`; box destination above. The pkarbs branch commit carries this report.