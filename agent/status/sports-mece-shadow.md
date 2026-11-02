# Status: sports-mece-shadow

State: OPEN
Last heartbeat: 2026-11-02 06:35Z
Output: shadow/data/ (raw, gitignored); status files under agent/status/

## What is done
- Shadow logger (shadow/shadow_logger.py) ran as a tracked background service (systemd scope pkarbs-shadow-logger.scope) for 8+ days. 7-day requirement COMPLETE (includes two full European-football weekends).
- Measured (committed status-2026-11-01): 6,742 runs / 1,314 distinct events with a run.

## What is blocked
- Daily sim `python3 shadow/shadow_sim.py --data shadow/data/ --one-way <t> --delays 0,1,3,market --max-usd 500` CANNOT complete: shadow_sim.py loads events.jsonl unconditionally (line 81) and the live file is 3.5 GB; there is no bounded-load / --limit option. Multiple attempts on one core exceed the memory cap.
- Requires: reviewer grant to add a bounded-load flag to shadow_sim.py (code change -> approval), OR a reviewer-provided bounded inputs route.

## Errors
- shadow_sim memory/OOM on the full 3.5 GB events.jsonl (see prior reports).

## Next
- Re-run sim on the completed 7-day window once a bound is available. Otherwise keep the logger running and heartbeat.
