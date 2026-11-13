# TO IT and Hermes, 13 Nov 12:55Z: do the Goalserve retest FIRST in the PK arbs row

Why first: the LoL Worlds final is on 14 Nov, and Goalserve esports data cannot be recovered afterwards. The retest is a 10-minute job.

Do this before the weekend perp smoke test:

1. Run `agent/inbox/2026-11-13-goalserve-retest-404s-with-exact-urls.md` (merged in PR #289).
2. Write `agent/status/goalserve-probe.md` with, for each request: URL (secrets redacted), HTTP status, body bytes after gunzip, first 200 characters, and whether it was a 404 or an empty 200.
3. If `inplay-esports.gz` returns data, start capturing it at about 0.5 s (see `agent/tasks/TASK-goalserve-v2-2026-11-12.md`), and say so in `agent/status/goalserve.md`.

Correction to the queue note: Goalserve is NOT blocked on the WebSocket token. The key is installed and the HTTP in-play files work. Only the WebSocket token is unresolved, and the esports test does not need it.

Reply by committing `agent/inbox/IT-REPLY-*.md` or commenting on issue #295.
