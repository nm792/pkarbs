# outbox: rugby nesting fix applied; D launched and verified (13:45Z)

RE: `agent/inbox/rugby-nesting-fix-approved-2026-11-08.md` — Nick approved the nesting fix (13:01:22Z); applied and launched per STEPS.

RESULT:
- Applied `rugby-top14-nesting-fix.patch` onto the origin vg2ckg copy of `rugby-top14-capture.py` (the flock-guarded one); `py_compile` passed; `grep -n flock` present (single-instance lock guard).
- Launched D at 13:45:05Z as a tracked background process (pid 133062, `python3 agent/tasks/rugby-top14-capture.py D`).
- Log line met note's bar: `tokens=6 markets=3` (D config = 6 clob tokens across 3 flat markets).
- Output verified within 60 s of launch: `rugby/D_clob.jsonl` 6 rows, `rugby/D_trades.jsonl` 34 rows, both present and growing; CLOB + SPORTS WS open.
- The older `rugby-top14-clob-fix.patch` (UA + watchdog) was NOT applied, per the note.

OPEN / NOT VERIFIED:
- Window C: same launch at 19:50Z from the patched copy; scheduled as a separate one-shot step, not yet due.
