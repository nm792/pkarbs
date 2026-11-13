# The main TheSports 2 h export (32295b: tennis, Dota, CS2, LoL) has NOT landed since 06:16Z 10 Nov

Your reply (11:27Z) says the 32295b export and diary are "covered by the live 2 h timer". Origin shows otherwise: last 32295b commit d8d0325fa @06:16:10Z; the 08:15Z, 10:15Z and 12:15Z runs are missing (ts_mqtt last chunk 06:00Z). The locked tennis (29/60) and Dota (13/40) tests are frozen on this, and the trial ends 16 Nov.

Please run the 32295b export NOW as a one-off (same layout, deletion guard) and reply in `agent/outbox/thesports-32295b-export-stalled-2026-11-10.md` with the commit sha, the last `ms` of markets.jsonl.gz and ts_mqtt, and why the timer runs after 06:16Z did not push (push race, dispatch gate, cron not firing, anything else). Then keep it running; this is the priority TASK (agent/tasks/TASK-thesports-export-priority-2026-11-10.md), ahead of the Netflix and chart recorders.
The cricket one-off is received, thank you. The card for the cricket timer wiring is with Nick.
