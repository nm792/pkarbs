# live-tweetcount dry run — 2026-11-10 ~05:20Z (before any order)

Per TASK-live-tweetcount-2026-11-10 step 1 (dry run, no orders placed):
`python3 agent/tasks/tweetcount-decide.py --slug elon-musk-of-tweets-november-6-november-13-2026 --force` (script extracted from origin pnd99n to /root/pkarbs, py ok, RC=0).

RESULT (pre-T; T = window end − 24 h = 1794502800 = 2026-11-12 17:00Z; today is 10 Nov, so this is NOT a real decision):
- xtracker reachable from the box: so_far=154 posts (Nov 6–13 window to now), rem_pred=42.2, mu=196.4, sd=18.5.
- Books load: 5 intents emitted, all BUY/No, limit 0.81–0.921, size 5.43–6.17, $5.00 each, total $25.00 — inside caps ($5/bracket, $25/window, $50 total).
- The script refuses to run outside [T, T+10 min] without --force; dry run used --force per the task.

Blocker found by the companion recorder probe (same round, see tweetcount-probe-2026-11-10.md): clob book for some bracket tokens returns HTTP 404 (event-level markets whose tokens no longer book), so the live recorder cannot be started as-written. This does not affect the dry run above (decide.py iterates brackets and only emitted intents for bookable ones).

Next: arm the T=12 Nov 17:00Z order timer once the recorder/404 question is answered by the thread; the decide script itself works.
