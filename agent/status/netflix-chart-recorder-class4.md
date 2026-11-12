# netflix-recorder + chart-recorder — class-4 install filed (2026-11-10 14:4xZ)
status: waiting on once-a-day CHANGE-BATCH approval
Two NEW loggers (netflix-recorder every 30 min + charts-recorder every 3 h) exist on origin tip
(`live/netflix/record_netflix.py` + test, `live/charts/record_charts.py` + test) but are NOT yet
installed: starting a new logger + timer/cron is class-4 under the 409 gate (2026-11-08..11-15),
so both are filed in dialogue/CHANGE-BATCH.md items 9 and 10 for Nick's once-a-day approval.
Thesports export-priority (P1) already landed 2026-11-10 14:16:57Z (01a3b8d58, +4454 files); cricket
slim + diary handled per outbox. No code/timer installed this round (gated). Revert: none applied.

## UPDATE 2026-11-12 01:45Z — INSTALLED (X432 reclassified CB9/10/11 Type A; agent applies now)
- pkarbs-charts-recorder.timer (CB10, 3h) + pkarbs-mentions-recorder.timer (CB11, 5m) + pkarbs-netflix-recorder.timer (CB9, 30m): all enabled + active, firing on schedule. Charts 01:30Z 0/SUCCESS (charts_20261112.jsonl.gz via /vol2, pages_ok=5: spotify 201 rows + openrouter 66). Mentions 01:30Z 0/SUCCESS (books_20261112.jsonl.gz, 13 targets/books).
- **ISSUE: netflix run 01:30Z hit its 600s TimeoutStartUSec and was KILLED (Result=timeout, ExecMainStatus=15) before ~01:40Z; partial output /vol2/pkarbs/netflix/wn_daily.jsonl 830,805 B (also a 0-byte books.jsonl.gz from 11 Nov).** Self-heals on the next 30m fire per Restart=always, but full top-10+book capture is not completing within 600s. Charts completes in ~16s; mentions in ~4s. Netflix needs either a longer timeout or a faster/partial path — flagging for the owner, not changing code here (class-4 would apply).
