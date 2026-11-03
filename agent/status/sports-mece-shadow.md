# Status: sports-mece-shadow

State: OPEN -> RUNNING (full 7-day bounded sim in flight, read-only replay)
Last heartbeat: 2026-11-03T00:48Z
Output: /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/ (raw); runs.jsonl growing (00:48Z); status under agent/status/

## What is done
- Shadow logger (shadow/shadow_logger.py) ran 8+ days. 7-day requirement COMPLETE (6,742 runs / 1,314 events).
- **Bounded-load fix APPLIED + VERIFIED (2 Nov, Nick-approved):** shadow_sim.py now takes --limit N / --days D; line 81 no longer loads the 3.7 GB events.jsonl unconditionally. Verified live: --limit 200 exit 0, ~40 MB RSS. Revert: shadow_sim.py.pre-bounded.
- **Concurrency resolved (2-3 Nov):** redundant duplicate sims killed earlier turn; exactly ONE bounded sim running now.

## In flight → EXITED
- Full 7-day shadow-sim run (proc 3272310, `--data data-v2 --one-way 0.05 --delays 0,1,3,market --max-usd 500 --days 9`), started 2026-11-03 00:28Z, has EXITED cleanly (no process, no OOM line). No `--per-run` CSV was passed, so its aggregate output went to stdout of the (now departed) tracked background session and is NOT recoverable from disk; runs.jsonl (7,784 rows, last row 2026-11-03 06:58:04Z) is the source data, not the results. Cannot reconstruct the sim's numeric P&L/edge without re-running with `--per-run`.
- Corrected path: re-run the same bounded load with `--per-run <csv>` to persist the analysis output, then post agent/outbox/shadow-sim-report.md. Needs a bounded re-run (read-only, no code change) — queued.
