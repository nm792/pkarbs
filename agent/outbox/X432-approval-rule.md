# X432 — approvals change (ack, 11 Nov 2026)

Acknowledged on the `claude/project-thread-vg2ckg` thread. This notice is now CHARTER clause 22 on trading-test/dialogue (Nick approved 02:24Z).

Operating rule confirmed for this project:

- **No approval needed:** server/data plumbing — new loggers and recorders that pass the disk gate + their tests, script/export/manifest/report fixes, crontab and unit changes for these, restarts, box ships. Run at once, report with SHA + revert.
- **Approval needed (your chat yes):** trading-decision, sizing, gate, entry, exit or orders; deleting data not on the box; keys and branches; paid spend. Written into dialogue as `APPROVED: <item>`, applied on next run.
- Server/agent problems go to `dialogue/TO-IT.md`.

This reply is the in-repo acknowledgment so the matcher reads the inbox note answered.
