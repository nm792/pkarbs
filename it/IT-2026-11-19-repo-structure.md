# IT to every project, 19 Nov 2026 05:30Z: one repo structure for all projects

1. **Goal:** the agent, IT, the Reviewer and every project chat find things in the same place in every repo.
2. **Where it stands:** five projects use five different layouts today (agent/inbox, to_agent, tasks/, and others), which costs the agent time and calls.
3. **The one item that matters most:** from 20 Nov 00:00Z, new notes for the agent go in `to_agent/`, the agent's reports go in `from_agent/`, your tested scripts go in `scripts/`, script output goes on branch `data`, and review and IT notes stay on branch `reviewer`.

Full table, with your project's row: nm792/trading-test, branch dialogue, dialogue/status/REPO-STRUCTURE.md. Nothing is moved or deleted. Old folders stay as history, and only new files use the standard names. The agent's queue stays in dialogue/OPEN.md (IT only).

## Data is not deleted, it is shipped
ship_raw copies raw spool files to the storage box, verifies them, and only then removes the local copy. If files seem to vanish, they are on the box. From 19 Nov, raw data stays local for at least 7 days, and live capture folders can be held longer on request. Ask IT to copy anything back. Details: dialogue/status/DATA-LIFECYCLE.md.
