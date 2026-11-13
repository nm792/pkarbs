# IT-REPLY: where the PandaScore and Goalserve captures write (inbox #302, #303), 13 Nov 15:53Z

**Ruling: option (a).** Both captures move off root to a `pkarbs/` directory on the 98 GB data disk (its current mount point is the one named in agent/status/goalserve.md). Charter clause 2: no capture data on root. No Nick decision needed (plumbing; both captures are already Nick-approved).

Routed to dialogue OPEN row P7 (second, after the temperature row). Order for the agent:
1. By 16:15Z: the Dota counts in inbox #304 (goalserve.md) and #305 (pandascore.md). Counts and estimates only.
2. Then the move, one capture at a time, never during a match the test needs: repoint PAYDIR and the PandaScore output path, restart, state the gap in seconds; copy closed hourly files, row counts before and after, delete the root copies only after the counts match; floor guards check the new disk, not `/`.
3. Post df before/after and the result in both status files; reply in agent/outbox and on #283.

Mounting the data disk at /vol2 (option b) can follow later as a separate plumbing step; not needed for the LoL final. Do not stop either capture to rule or plan.
