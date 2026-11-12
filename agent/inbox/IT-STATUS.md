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
