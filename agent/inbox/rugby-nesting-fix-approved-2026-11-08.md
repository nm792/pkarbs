# APPROVED (Nick, 13:01:22Z 8 Nov, decision card "Apply fix, launch D from it"): apply the nesting fix

Apply `agent/tasks/rugby-top14-nesting-fix.patch` to the project-thread-vg2ckg copy of rugby-top14-capture.py (the one with the flock guard) and launch window D at 13:45Z from it. Steps and checks are in `agent/inbox/rugby-nesting-fix-2026-11-08.md`.
Report in agent/outbox/rugby-nesting-fix-2026-11-08.md: the `tokens=6 markets=3` log line, and that rugby/D_clob.jsonl and rugby/D_trades.jsonl exist and grow within 60 s of launch. Same for C at 19:50Z. Do not apply the older rugby-top14-clob-fix.patch.
