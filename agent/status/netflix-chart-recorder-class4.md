# netflix-recorder + chart-recorder — class-4 install filed (2026-11-10 14:4xZ)
status: waiting on once-a-day CHANGE-BATCH approval
Two NEW loggers (netflix-recorder every 30 min + charts-recorder every 3 h) exist on origin tip
(`live/netflix/record_netflix.py` + test, `live/charts/record_charts.py` + test) but are NOT yet
installed: starting a new logger + timer/cron is class-4 under the 409 gate (2026-11-08..11-15),
so both are filed in dialogue/CHANGE-BATCH.md items 9 and 10 for Nick's once-a-day approval.
Thesports export-priority (P1) already landed 2026-11-10 14:16:57Z (01a3b8d58, +4454 files); cricket
slim + diary handled per outbox. No code/timer installed this round (gated). Revert: none applied.
