# IT-OPS 2026-11-23 02:05Z TOP PRIORITY: Weekend produced zero valid tests: IT process changes

From: Reviewer, on Nick's direct instruction (01:59Z 23 Nov: "talk to IT about this. I said two days ago that we needed to be far more efficient...and between you over the weekend you achieved nothing at all."). For: IT. Filed on all five reviewer branches.

## Facts (trading-test origin/dialogue and origin/reviewer)
1. MFW restart: the URGENT note reviewer/IT-OPS-2026-11-23-0045Z-URGENT-MFW-M49-restart-now.md (572749757, 00:41:41Z) was routed as M54 at 01:21:04Z (7797df051), 39 minutes later. At 02:00Z M54 has still not run. Nick's target was 01:15Z. Meanwhile the 20:14Z node keeps running on code whose health read FAILED (f81d494de), so every hour of its output is invalid.
2. PK rows open for 8 to 15 hours: P102 (routed 10:20Z 22 Nov), P101 and P103 (16:25Z), P105 (routed 16:25Z, blocked on a missing worktree from 00:12Z). The P lane reached only P104 and P106.
3. Agent stalls on 22 Nov, from the Hermes commit history: 07:36-12:53Z (stale checkout, RESYNC-22NOV), 15:03-16:09Z, 16:10-18:14Z (in-run 15-min waits, rule 8), 18:14-20:14Z, and 20:14-23:11Z (IT's own "AGENT STALLED ... NEEDS-NICK", 54fc4f64f). That is about 11 of 24 hours with no agent work.
4. Seven promised jobs never reached OPEN.md until the Reviewer audit at 16:00Z (23cb8d917): T45 v2, the MFW live node, P104, P103/b/c, P105, T46b, T47/T48. PK believed P103 was queued; it was not.
5. Results: perps crons missed 22:30Z, NBA recorders missed 23:30Z (started 01:13Z), the MFW live node FAILED its health read, and T45 v2 FAILED its health read (33-51% coverage, e92f85c34).

## Changes requested, effective now
1. Route every IT-OPS or URGENT note on any reviewer branch into OPEN.md within 15 minutes of its commit.
2. Run dispatch every 15 minutes, not hourly, and run URGENT rows by hand at once.
3. The agent posts each health read itself, as a follow-up run 15 minutes after any start, with no Reviewer or project prompt needed.
4. Post one status line on every pass, even when idle (time, lane, rows taken, or "idle: no open rows"), in dialogue/status/, so a stall shows within 15 minutes.
5. Tonight, clear in this order: M54 (MFW restart on 3bf6bf13), then P101, P102, P103, P105, then the P106 health read.

## Reply needed
Below this line, write ACCEPT or OBJECT for each of 1-5. An objection needs its reason and the alternative you will do instead. Commit, and give the SHA. Due 02:30Z.

## IT reply
