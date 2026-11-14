# URGENT to IT: Hermes is looping on the PandaScore restart gate; two tasks 9 h overdue

From: the Goalserve/feeds thread. Date: 14 Nov 2026, 16:00Z. Escalated under Nick's standing rule (Hermes stalls go to IT, not to Nick). Coordinator asked for this at 15:58Z.

## What I observed (commit log, nm792/pkarbs)

1. Between 14:09Z and 15:53Z, Prime Bot made 12 commits about the #339 PandaScore 4004 retry-loop fix. Every one is a recheck of the "safe restart gate" (14:18, 14:38, 14:52, 15:02, 15:13, 15:23, 15:33, 15:42, 15:53Z and others). Each found live matches and held the restart. The fix is staged, not applied; the 4004 retry loop is therefore still running.
2. Two tasks have had no reply in the repo since they were filed:
   - #323 Goalserve cricket URL probe (due 07:00Z, about 9 h overdue).
   - #324 TheSports cricket 48h capture vs Polymarket overlap count (due 06:30Z, about 9.5 h overdue).
   Nick asked on 14 Nov 04:25Z to find the cricket feed. BBL starts 12 Dec and is at risk.

## Asks, with deadlines

A. Rule a restart window for the PandaScore 4004 fix: either a fixed gap between matches (tonight) or a rule such as "restart when no live PandaScore match for 10 minutes, no later than 16 Nov 12:00Z, before BLAST on 17 Nov". Once ruled, Hermes should stop rechecking the gate. Reply by 17:00Z.
B. Direct Hermes to do #323 and #324 before any further gate work, one chunked task each, in this order: #324 count (count-only, no verdict), then #323 probe. Both reports by 20:00Z.
C. Confirm in your reply whether the 17:00Z and 18:30Z LoL final proofs (PR #317, #341) are still scheduled ahead of both items. The final starts 19:00Z.

I will check the repo at 17:05Z and report to the coordinator whether A is ruled, and at 20:05Z on B. No Nick approval is needed for A or B (script restarts and tasks are Type A, clause 22A).
