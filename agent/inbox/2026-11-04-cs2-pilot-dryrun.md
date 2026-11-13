# Hermes: CS2 pilot dry run (new task, no key, no orders)

Task file: agent/tasks/cs2-pilot.md. Nick approved building the capped CS2 pilot (4 Nov 06:34Z) and asked for a dry run
on live markets before any live order. This is protocol-compliant (read-only, single bounded process, logger-like),
so please start it on your next poll once this PR is on the default branch. It runs alongside the always-on loggers.

Please do NOT install or ask for any trading key, and never create LIVE_OK: both are Nick's own steps
(live/cs2_pilot/KEY-INSTALL.md). First thing to report in agent/status/cs2-pilot.md: the geoblock line from the
`start` row of pilot.jsonl (country and blocked true/false).
