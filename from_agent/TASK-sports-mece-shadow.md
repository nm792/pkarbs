# TASK-sports-mece-shadow — bounded-load applied, sim unblocked (from_agent)

## APPROVALS
- bounded-load change to shadow/shadow_sim.py: APPROVED by Nick at ~15:5xZ 2 Nov (raised via the
  approval interface). Applied.

## RESULT
- shadow_sim.py now accepts `--limit N` (max events from events.jsonl) and `--days D` (+ `--now`)
  to bound the load. Line 81 no longer loads the whole 3.7 GB events.jsonl unconditionally; runs
  whose legs/event fall outside the loaded slice are dropped (not crashed) when a limit is set.
- py_compile OK. Verified live on the REAL capture data
  (/mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/, 3.7 GB events.jsonl):
  `--limit 200` -> **exit 0**, ~40 MB peak RSS, 11-12 runs per side processed, full report lines
  written per delay (side yes/no/both x delays 0/1/3). Previously any capped attempt OOM'd on the
  full file.
- Revert: restore shadow/shadow_sim.py.pre-bounded.

## DATA
- File: /root/pkarbs/shadow/shadow_sim.py (bounded-load). Backup: shadow_sim.py.pre-bounded.
- Verified run: data-v2, --limit 200, one-way 0.05, delays 0,1,3, max-usd 500, exit 0.
- The 7-day shadow capture itself is COMPLETE (6,742 runs / 1,314 events).

## OPEN / NOT VERIFIED
- The full daily sim over the completed 7-day window is now runnable but NOT yet run end-to-end on
  the whole window (that is a compute step I can do next; it is read-only replay, no live trading).
  Recommend a single bounded run with `--days` across the completed week, then a report.

## Count
notes run 1 (bounded-load applied + verified), outstanding 1 (full-window sim + report), PENDING closed.

## Context
pkarbs sports-mece-shadow. Unblocks the daily sim that was frozen on events.jsonl memory since 29 Oct.
Shadow replay only. No IPs/host/volume names.
