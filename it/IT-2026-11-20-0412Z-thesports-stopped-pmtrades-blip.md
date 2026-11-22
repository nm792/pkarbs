# IT 04:12Z 20 Nov: TheSports exporter off; brief trades.jsonl gap to check

Goal: keep your protected recorders whole while VOL2 recovers.

Position (live session ~03:58Z, relayed by Nick):
- No thesports-capture-b unit exists and no TheSports capture process was running.
- The TheSports export-timer cron line is now commented out. That was the exporter, export_slim_32295_plumb.py.
- VOL2 had 12.26 GB free at 03:58Z, roughly flat.
- Nothing was shipped or deleted.

The one item for you: the session stopped thesports-pmtrades.service by mistake. That service writes trades.jsonl. It restarted, and is active with trades.jsonl growing again, but there is a short gap around 03:40-03:58Z. Please check trades.jsonl for that window and tell IT here if it matters.

Next: T0k2 ships the dead TheSports output (every file under pkarbs/thesports except books, markets, trades and pmws, and anything a process holds open) to the box. It verifies the checksums, then deletes only the verified local copies, aiming for VOL2 above 25 GB free. Reply here if any of that output is still needed.
