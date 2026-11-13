# Task for the server agent: STOP all scans now and free the RAM (do this first)

From: Claude in the "PK arbs" project, on Nick's instruction (25 Oct 2026, 02:01Z).
Status: DONE
Priority: do this before any other task in agent/.

## What to do
1. Kill every running rescan, sim, analysis or backfill process for this repo, including any
   `shadow/rescan.py`, `shadow/shadow_sim.py`, daily-report sims, and any other Python job reading
   `shadow/` data. Use `ps aux --sort=-rss` to find them.
2. **Keep exactly one process running: the live v2 logger** (`shadow/shadow_logger.py` writing to
   `shadow/data-v2/`). Do not stop or restart it. If more than one logger is running, keep the one
   writing to `shadow/data-v2/` and kill the rest.
3. Suspend the daily `shadow_sim.py` report in `agent/TASK-sports-mece-shadow.md` (step "Daily report").
   Do not run it again until a new task says so. The logger part of that task continues.
4. Do not start any new scan, rescan or sim until a task in agent/ with Status OPEN asks for it.

## Report (commit to this repo within the hour)
Commit `reports/sports-mece/stop-2026-10-25.md` with:
- every process killed: PID, command line, RSS in MB, and how long it had been running;
- the logger process kept: PID, command line, RSS, and the newest raw file it is writing;
- `free -m` before and after.

Set Status above to DONE and commit.
