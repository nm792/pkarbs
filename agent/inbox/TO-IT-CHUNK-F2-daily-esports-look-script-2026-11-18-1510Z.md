# CHUNK F2: the daily esports look as one script (REPLACES the command in chunk F). Read-only. Posted 18 Nov 2026 15:10Z. First run 19 Nov after 00:30Z.

**1. Goal.** First daily Goalserve esports look in the free trial; Nick wants it checked now, not on 25 Nov.
**2. Why a new command.** Chunk F said "use the E2 command with a per-day poll log". That fails: the capture fixes the poll-log name at start, so 18 Nov and later polls are in `goalserve_20261117.jsonl` and there is no `goalserve_20261118.jsonl` (chunk H, 4908eea2a6). A per-day poll-log argument would read no polls and stop. The script reads all `goalserve_20*.jsonl`, uses the clean export (no stash, no pull), and the recorder dir `final-topics-32295b`. Signed code: d3a8849a or later (esports path unchanged by the tennis commit, checker Addendum 2). Tested end to end here on fake data (look 2, plants recovered).
**3. The one item.** Once a day, after 00:30 UTC, starting 19 Nov (expected look 1), with RSYNC_RSH and BOX_ROOT set as before:
```
V=/mnt/HC_Volume_107257520; mkdir -p $V/tmp
git -C /root/pkarbs fetch -q origin claude/project-thread-vg2ckg && git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:feeds/run_daily_look.sh > $V/tmp/run_daily_look.sh
nice -n 10 bash $V/tmp/run_daily_look.sh esports
```
Post, appended to agent/status/goalserve.md under `## F look K (date)`: the whole stdout of the script (it prints exactly the fields to post: date, free bytes, commit and sha256 lines, self-test tail, hour-file counts, poll logs, PM last row, run exit, result sha256, counters, plain_summary, the primary cell line and first20). Copy the result file to `agent/status/goalserve-esports-look<K>-<date>.json`.
Gates are inside the script (disk above 15 GB, export, self test tail must say ALL PASS, K at least 1). If a line says STOP or a hour-file count for a past day is below 24, post it as it is; do not fill gaps.
**Done check:** `run exit 0`, `smoke_not_a_result false`, `look` equal to the printed `look_expected`, `plant_c 0.01`, result sha256 matches the copied file.
**Stop:** after look 20 (8 Dec) or when this thread says so.
