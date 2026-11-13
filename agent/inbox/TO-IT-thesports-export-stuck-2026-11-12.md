# TO IT: TheSports export stuck, Nick asked for escalation (12 November 2026, 01:50Z)

Nick's words: "raise this stuff with IT. you cannot just leave everything to moulder overnight."

This is the pkarbs side of OPEN row E in trading-test dialogue/OPEN.md. Please copy it to dialogue/TO-IT.md if that is where IT reads, because the pkarbs thread cannot write to trading-test.

**What is stuck**
- No TheSports data has reached origin/claude/project-thread-vg2ckg since 10:00Z on 11 November (newest ts_mqtt chunk 1794384000000, markets.jsonl.gz still 2,374 rows). That is about 16 hours.
- Tennis test T1 is at 59 of 60 matches and Dota test D1 at 28 of 40 games. The locked, pre-registered tests cannot run until the data lands.
- The agent's hand export (started 21:04Z, 43,670 files, pid 3608478 as of 23:40Z) has not pushed and has not reported since 23:40Z.
- Earlier pushes failed on the non-fast-forward race (fixed in de0517c84 at 19:26Z), and one manual push (b5193c0b3, 15:18Z) was an empty commit.

**Deadline**
- The TheSports free trial ends 16 November. No paying or extending. Tennis and Dota must be settled inside it.

**What we need from IT now**
1. Check on the server whether pid 3608478 (export_timer_2h.sh, flock thesports-slim.lock) is alive, hung or dead, and whether the push is waiting on something.
2. If it is hung or dead, get the export built and pushed as one fast-forward commit, then confirm the newest ts_mqtt chunk on origin is later than 1794384000000.
3. Confirm the next timed 2-hour export also lands.
4. VOL2 is at 7.7 GB free, below the 15 GB floor (OPEN row D). Please make sure that is not what is stalling the build.

We checked this repo every 30 minutes. Next pkarbs check is 02:15Z.

**Update 03:30Z:** the export landed at 03:05Z (f80025b293, +43,651 files). This note is kept for the record.
