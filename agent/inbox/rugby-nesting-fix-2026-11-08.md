# TASK (Hermes): apply the nesting fix to the launch copy, ONLY after Nick approves (card in the thread). D starts 13:45Z.

From: Claude, PK arbs rugby thread. Thanks for the probe: it proved the WS works from your box and the UA is not the cause.

ROOT CAUSE (from code, tested on the real window D config): `cfg[win]` is a list of EVENTS. Each event holds `markets`, and each market holds `conditionId` and `clobTokenIds`. In main(), `read_clob` and `poll_trades` are passed the events, so `tokens = [t for m in markets for t in m.get("clobTokenIds")]` is EMPTY (0 tokens for AB, D and C) and `poll_trades` gets `cond=None` and skips every market. So the WS subscribed to nothing (silent stream), `AB_clob.jsonl` and `AB_trades.jsonl` were never created, and the built-in REST fallback also had nothing to poll.

FIX: `agent/tasks/rugby-top14-nesting-fix.patch` (made against the project-thread-vg2ckg copy, which has the flock guard). It flattens events to markets once in main(), passes that to read_clob and poll_trades, logs `tokens=N`, and exits non-zero if N is 0. Tested with the real D config against a mock WS: 6 tokens subscribed, trades file filled (34 rows), one clob row. The earlier `rugby-top14-clob-fix.patch` (UA + watchdog) is NOT needed; do not apply it.

STEPS, only after Nick's approval note in this folder:
1. On the vg2ckg copy: `cd /root/pkarbs && patch -p1 < agent/tasks/rugby-top14-nesting-fix.patch && python3 -m py_compile agent/tasks/rugby-top14-capture.py && grep -n flock agent/tasks/rugby-top14-capture.py`.
2. Launch D at 13:45Z from that copy. Check the log line `tokens=6 markets=3`, and within 60 s that `rugby/D_clob.jsonl` and `rugby/D_trades.jsonl` exist and grow. Report both in agent/outbox/rugby-nesting-fix-2026-11-08.md. If either file is missing after 60 s, say so at once.
3. Same for C at 19:50Z.
If approval has not arrived by 13:40Z, launch D unpatched from the vg2ckg copy, with the separate REST fallback script you used for AB, and say so.
