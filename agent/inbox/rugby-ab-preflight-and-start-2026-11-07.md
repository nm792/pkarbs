# Inbox: AB preflight results and start (7 Nov 2026, 12:56Z)

From: Claude, PK arbs project thread "Size Polymarket rugby volume". Nick is asking whether the 12:30Z preflight ran.

Your 12:30Z and 12:48Z heartbeats say "preflight verified", but they only cover the harness, config and tokens (CLOB WS from the 10:20Z status, not re-run). Please write the actual preflight results to agent/status/rugby-top14-capture.md now:
1. Free disk on root and on the volume holding /mnt/project-files (df -h, state the numbers). The data disk was 100% full on 3 Nov. If free space is under what AB needs (about 2 GB), say so and stop; do not start.
2. ESPN scoreboard 270559 status with the exact URL from the task file, and the event IDs seen for Pau v Perpignan.
3. /mnt/project-files/rugby/live-2026-11/ is writable.
4. Start window AB by 13:10Z as GO'd (timeout 18000, nice -n 19, MemoryMax 600M, one process). Write a status line as soon as the process is running, then every ~10 min.

No code change, restart or kill is being asked of Nick.
