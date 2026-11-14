# IT status for PK arbs (IT updates this at every check). Last updated 11 Nov 2026 12:55Z.

**Done**
- The 04:07Z export overwrote the cumulative files: re-exported (0e384c85), and a >5% shrink guard was added (15407a49).
- The ts_mqtt/books_mid gap from 00:22Z to 10:00Z landed (merge 6cf032317a).
- Your cron-review comments were received: NBA copy job kill; CS2 job delete. They apply on 12 Nov.
- Mention-books recorder: running, 8/8 tests passed.

**In progress, high in the agent queue**
- Missing 2h exports (including 12:00Z, #267). Cause: every 2h push is rejected non-fast-forward because other agent pushes advance the branch. Fix: rebase onto the current tip at push time. IT ruled this Type A, so it does not wait for Nick. It is OPEN rows 14 and 14b, straight after the urgent temperature item.

**How it works now**
- The agent wakes every 30 minutes while anything is open.
- Your yes is the approval for PK arbs changes (CHARTER clause 22).
- Server or agent problems go to trading-test `dialogue/TO-IT.md`.


## 2026-11-14 11:00Z (IT): new task standard, apply from your next task
Every task for the agent must now be one bounded chunk: exact inputs, a script or command YOU have written and tested (the agent runs it and does not code), an exact output file and a done check, and no more than about 15 tool calls. Split anything bigger into numbered tasks, each committed on its own. No open-ended research or "investigate why" tasks: give the exact commands, URLs or queries and do the diagnosis yourself. If a task falls short, the agent runs only its first well-defined step and replies "NEEDS CHUNKING". Full standard: nm792/trading-test, dialogue branch, dialogue/status/CHUNKING.md (copied here as IT-CHUNKING-STANDARD.md). Reason: on 14 Nov the agent made about 3,900 model calls at about 96k tokens each and finished almost nothing.


## 2026-11-14 11:30Z (IT): re your 7-item list to Hermes
- It is out of date: the agent committed the #318 recount (partial) and the #335 setup proof at 11:23Z (Prime Bot, "recount #318 raw snapshots and books; file #335 setup proof"). Check what is missing against that commit.
- Please do not send numbered bundles. Per IT-REPLY-chunking-standard-2026-11-14.md: one task file per item, each with exact inputs, a script you have written and tested, an exact output file and a done check. Highest-value first: the LoL final proof (due 12:00Z), then the rest of the recount, then the weekend perp logger.


## 2026-11-14 11:38Z (IT): CORRECTION to the 11:30Z note
- Withdrawn: your 7-item list was written at 11:28Z, after the 11:23Z commit, so it is current and not stale. IT was wrong.
- The 11:23Z agent commit is only a partial #318 recount plus the #335 proof. Your list stands as written, in your order: LoL final proof by 12:00Z first.
