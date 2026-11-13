# COPY NOW: LoL pilot DK-BLG data (no hourly copies under live/lol_pilot/runs/ yet)

DK-BLG is over. Please, as one bounded step:
1. Run `python3 live/lol_pilot/speed_report.py /root/lolpilot/out/pilot.jsonl` and `python3 live/cs2_pilot/report.py /root/lolpilot/out/pilot.jsonl`; paste both outputs into `agent/status/lol-pilot.md`.
2. Copy (gzip) `pilot.jsonl`, `books.jsonl`, `summary.json` to `live/lol_pilot/runs/2026-11-05/` and commit. If books.jsonl is over 90 MB gzipped, split by hour.
3. Leave the process running: it stays up for T1 vs KC (22:00Z today). Still DRY ONLY.
Reply in `agent/outbox/2026-11-06-lol-pilot-copy-now.md`.
