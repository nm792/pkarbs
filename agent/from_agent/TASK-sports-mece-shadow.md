# TASK-sports-mece-shadow — logger already running as a service (no button needed)

## APPROVALS NEEDED
- none — the GATED "start the logger" step is already satisfied; no button should be raised.

## STATUS
The shadow logger is **already running as a systemd service** — no start needed, and starting a second instance would corrupt the 7-day shadow data.

- **Service:** `pkarbs-shadow-logger.scope` — `ActiveState=active`, entered **2026-10-25 02:51:41Z** (3d 23h uptime).
- **Command:** `/usr/bin/python3 shadow/shadow_logger.py --out /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/` (defaults: in-play 4h, gamma 120s, REST 60s, min edge 0; no `--lead-h`).
- **Data flowing:** `events.jsonl` = 1.77 GB (updated 02:24Z); `runs.jsonl` = 2.19 MB (updated 01:06Z); 2 files written in the last 5 min.
- **Process:** pid 2951556, 737 CPU-minutes, running since Oct 25.

The cron's "GO NEEDED: start the logger" is stale — the service has been up since 25 Oct. No button raised.

## OPEN / NOT VERIFIED
- Daily report (`reports/sports-mece/YYYY-MM-DD.md`) is due — will run `shadow_sim.py` and commit today's report.

## Count
notes run 1 (TASK-sports-mece-shadow), outstanding 0, PENDING open 0.
