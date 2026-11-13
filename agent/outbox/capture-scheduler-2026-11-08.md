# Reply: capture-scheduler-2026-11-08.md

From: Hermes (server member), round 2026-11-08T23:14Z

Read-only dry-run outputs (per request; NO install, NO schedule rows added).

`python3 agent/tasks/capture_launcher.py rugby --window C --dry-launch` →
```
{"step": "check", "kind": "rugby", "window": "C", "events": 1, "markets": 3, "tokens": 6, "book_rest_fail": [], "check": "PASS", "t": "2026-11-08T23:13:55Z"}
{"step": "dry-launch", "cmd": ["/usr/bin/python3", "-u", "/root/pkarbs/agent/tasks/rugby-top14-capture.py", "C"], "t": "2026-11-08T23:13:55Z"}
```
Check: PASS — 1 event, 3 markets, 6 tokens, no book REST failures. Dry-launch shows the exact command that would fire (rugby-top14-capture.py window C) but did NOT launch.

`python3 agent/tasks/schedule_captures.py --list` →
```
NEXT LEFT LAST PASSED UNIT ACTIVATES
0 timers listed.
```
No schedule timers exist yet (expected — captures-schedule.json is empty, no rows added).

systemd-run transient-timer capability test (systemd-run --on-active=30 + systemctl list-timers + stop): NOT RUN. This headless cron run cannot execute systemd-run/systemctl (consent-gated without an interactive user). That capability check must be confirmed from an interactive session or run directly on the box; do not assume transient timers work until that test passes on the box.

Item 3 (chess next game start times): I do not hold chess (WCC) match start times in any artifact. Provide the schedule or a source and I'll add rows.

Install (`--install` / adding capture rows) is NOT performed — awaiting Nick's card approval per the task's gate.
