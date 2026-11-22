# PROTOCOL: Reviewer dialogue (from 20 Nov 2026, Nick 06:48Z)

Response window 15 minutes (Nick 06:50Z). Why: communication delays cost at least 3 project hours on 20 Nov. From now on, every exchange goes through two append-only files on this `reviewer` branch.

## Files (folder `reviewer/pkarbs/`)
- `INBOX.md`: project to Reviewer. Only the project writes here.
- `OUTBOX.md`: Reviewer to project. Only the Reviewer writes here.
- Append only. Never edit or delete a row. To change a status, append a new row with the same ID. The last row for an ID is its current status.

## Row format (one line per row, pipes exactly as shown)
`| ID | UTC | status | ref | summary |`
- INBOX IDs: `P-001`, `P-002` and so on. Status `open` when posted; the Reviewer never changes it.
- OUTBOX IDs: `R-001`, `R-002` and so on. Status `answered`. `ref` names the INBOX ID it answers (or `-` for an order). The answer file or commit goes in `summary`.
- Ack: the project appends to INBOX `| R-00n | UTC | acked | <commit or -> | one line |`, using the OUTBOX ID.
- UTC is written as `2026-11-20T06:50Z`.

## Rules
1. A project posts every question, result or request as a new `open` INBOX row. A longer REPLY file may still be attached: name it in `summary`.
2. The Reviewer watches every INBOX continuously (fetch every 2-3 minutes; hourly backstop). Each open row goes at once to the owning review thread, which answers in OUTBOX within 15 minutes.
3. The project acks each OUTBOX row by ID in INBOX before acting on it. The Reviewer reports work as started only after an ack and a project commit, never on the strength of an order alone.
4. Any INBOX row open for more than 15 minutes, or any OUTBOX row unacked for more than 15 minutes, goes to the coordinator, who escalates to Nick.
5. The other rules are unchanged: SETTLED.md, REPLY-RULES.md (goal, measured position, top item), and no writes to agent-read paths by the Reviewer.
