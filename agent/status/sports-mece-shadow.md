# Status: sports-mece-shadow

State: OPEN -> UNBLOCKED (bounded sim run verified); full-window sim next
Last heartbeat: 2026-11-02 ~15:5xZ
Output: shadow/data/ + /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/ (raw); status files under agent/status/

## What is done
- Shadow logger (shadow/shadow_logger.py) ran 8+ days. 7-day requirement COMPLETE (6,742 runs / 1,314 events).
- **Bounded-load fix APPLIED + VERIFIED (2 Nov, Nick-approved):** shadow_sim.py now takes --limit N /
  --days D; line 81 no longer loads the 3.7 GB events.jsonl unconditionally; runs outside the loaded
  slice are dropped, not crashed. Verified live on data-v2: `--limit 200` exit 0, ~40 MB RSS, full
  per-delay report lines. Revert: shadow_sim.py.pre-bounded.

## Next
- Run the daily sim over the completed 7-day window (single bounded run, `--days`, read-only replay)
  and produce the report. This is the last unblocked step.

## Errors
- Previous sim attempts OOM'd on the full 3.7 GB events.jsonl (no bound). Resolved by the fix above.

## Long-term (outside this task)
- sports-mece live scoring stays separate; shadow only until scored.
