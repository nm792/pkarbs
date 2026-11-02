# Inbox: run the Nepal PL ball-by-ball capture, 3 Nov 06:30Z and 10:30Z

From: project thread (PK arbs), 2 Nov 2026 15:30Z
To: server agent (Hermes)

Nick asked for live cricket timing (2 Nov 15:22Z). Please run `agent/tasks/TASK-cricket-npl-live-2026-11-03.md`: two bounded runs of `evrules/live_pbp_logger.py`, using the code that is already merged. This is task-compliant work, with no code change and no restart of anything else, so Nick is not needed.

Please:
1. Confirm pickup in `agent/outbox/2026-11-02-cricket-npl-live.md` before 06:00Z on 3 Nov, using a dry run: `--minutes 0.2` on id 1558592 (yesterday's match), and say how many rows it got.
2. Run windows A and B as written.
3. Report as the task says.
