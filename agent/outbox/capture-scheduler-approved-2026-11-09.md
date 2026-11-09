# agent/outbox — capture-scheduler approved install (Nick card 2026-11-09 00:19:32Z)

## APPROVALS NEEDED
- none for the run itself. Nick tapped "Yes, install and add rows" (00:19:32Z card). The
  schedule_captures.py --run-due call is added to the dispatch loop. No captures yet scheduled:
  captures-schedule.json entries are EMPTY (0 timers listed; --run-due no-op until rows land).

## RESULT
- Pulled files OK: agent/tasks/schedule_captures.py (present on origin thread, 53 lines) and
  agent/tasks/captures-schedule.json (entries []). Verified by extracting from origin and running.
- --list: "0 timers listed" (no systemd timers; --run-due mode needs no systemd, fires only when a
  row's fire time passes).
- One dry-launch/run-due check with empty schedule: prints nothing to launch (no rows -> no-op, safe).
- last_launch.txt: not created yet (nothing launched; will copy into agent/status/rugby-top14-capture.md
  after the first real launch).

## OPEN / NOT VERIFIED
- Rows will be added by the rugby thread as the next Top 14 windows and chess WCC game times are known.
  Until then --run-due is a no-op each round.

Count: notes run 1 (capture-scheduler-approved), outstanding 0, PENDING open 0.
Context: server-member dispatch round 2026-11-09 ~01:2xZ.
