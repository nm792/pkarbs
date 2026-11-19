# CHUNK K: the daily tennis look. Read-only. Posted 18 Nov 2026 15:10Z. First run 20 Nov after 00:30Z (tennis counts from 19 Nov 00:00Z).

**1. Goal.** Time Goalserve tennis in-play odds against the Polymarket price in the free trial, in parallel with esports (Nick, 08:04Z).
**2. Position.** Tennis path signed for code (checker, 12:13Z, squash 09b9665e). Chunk J (7e6b911daf): smoke exit 0, 1,575 events in two hours, 43 matches with events, Polymarket name candidates 0/1/2+ = 13/30/0, market "To Win". Same script as chunk F2, argument `tennis`.
**3. The one item.** Once a day after 00:30 UTC from 20 Nov, same environment as F2:
```
V=/mnt/HC_Volume_107257520; mkdir -p $V/tmp
git -C /root/pkarbs fetch -q origin claude/project-thread-vg2ckg && git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:feeds/run_daily_look.sh > $V/tmp/run_daily_look.sh
nice -n 10 bash $V/tmp/run_daily_look.sh tennis
```
Post, appended to agent/status/goalserve.md under `## K look K (date)`: the whole stdout of the script (it prints exactly the fields to post: date, free bytes, commit and sha256 lines, self-test tail, hour-file counts, poll logs, PM last row, run exit, result sha256, counters, plain_summary, the primary cell line and first20). Copy the result file to `agent/status/goalserve-tennis-look<K>-<date>.json`.
The script stops if the data volume has under 15 GB free; stored tennis hour files are about 1.9 GB a day, so say the free bytes every day. Run it after the esports look, never in parallel with it.
**Done check:** `run exit 0`, `sport "tennis"`, `smoke_not_a_result false`, `look` equal to `look_expected` (20 Nov = 1), result sha256 matches the copy.
**Stop:** when the primary cell line says the cell is closed (100 matches) or after look 20, or when this thread says so.
