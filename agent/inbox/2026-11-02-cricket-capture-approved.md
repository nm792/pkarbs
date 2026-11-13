# Inbox: approved, keep cricket too (restart allowed)

From: project thread (PK arbs), 2 Nov 2026 14:35Z
To: server agent (Hermes)

Nick approved this in the project chat at 14:35Z with "yes".

You may edit the CS2 WS logger and restart it so it saves cricket and other sports messages as well as CS2. This is the change from `agent/inbox/2026-11-02-ws-keep-all-messages.md`: remove the `leagueAbbreviation !== 'cs2'` filter in `logger.js`, then restart the `cs2-logger.scope`.

Keep these limits from the task:
- Single process, `timeout 43200`, `MemoryMax=512M`.
- Keep the CS2 output files and the log running. Write cricket to its own file or tag each line with its sport, so the two can be separated later.

Please do the following:
1. Confirm the restart in `agent/status/cs2-ws-logger.md`, with the time and the new process ID.
2. Confirm that cricket messages are being saved, with one example line and the file it went to.
3. Reply in `agent/outbox/2026-11-02-cricket-capture-approved.md`.

Nick is not needed again for this step.
