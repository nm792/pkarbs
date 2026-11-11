# X432 — Change in how approvals work (11 Nov 2026)

Nick approved this at 02:24Z. It is now in CHARTER clause 22 on trading-test/dialogue.

- **No approval needed:** server and data plumbing. That covers new loggers and recorders that pass the disk gate and their tests, script, export, manifest and report fixes, crontab and unit changes for these, restarts, and box ships. The agent does this work at once and reports it with the SHA and the revert.
- **Needs approval:** a change to a trading decision, sizing, gate, entry, exit or orders; deleting data that is not on the box; keys and branches; paid spend. **Your yes in this chat is the approval for this project.** Write it into the dialogue as "APPROVED: <item>" and the agent applies it on its next run. It does not wait for Nick's daily batch.
- Server or agent problems still go to trading-test dialogue/TO-IT.md.
