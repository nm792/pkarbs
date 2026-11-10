# TASK: record free Spotify (kworb) and OpenRouter chart pages every 3 hours (10 weeks)

From: Claude in the PK arbs thread "Find and test MrBeast-style markets" (10 Nov 2026, 11:00Z). Requested by Nick (free sources only, keep working across categories). Status: OPEN. Do it right after TASK-netflix-recorder (same pattern, separate timer).

## Why
No free history exists for Spotify daily/weekly charts or OpenRouter weekly rankings (Wayback has the pages but the fetch tool strips song names). Polymarket lists ~110 weekly Spotify events a year ($115M total). A forward record is the only way to test a within-week model with strict availability.

## Question (one only)
Does `live/charts/record_charts.py` run on the server and save the five pages with names intact?

## Pass / fail, fixed before running
- PASS: `python3 live/charts/test_record_charts.py` prints `5 of 5 checks pass`; the first real run writes `charts_YYYYMMDD.jsonl.gz` with 5 lines, `status` 200 and `n_rows` >= 50 for at least the four kworb pages; stdout ends with `"ev": "done"`.
- FAIL: anything else. Report the last 20 lines and stop. No retries beyond one. If only OpenRouter fails (JS-only page), still PASS the kworb pages and say so.
- Read-only HTTPS, 5 requests per run, 3 s apart, robots.txt allows both sites. No keys, no orders.

## Run
```
cd <repo> && git pull
python3 live/charts/test_record_charts.py
mkdir -p /root/charts/live
timeout 300 python3 live/charts/record_charts.py /root/charts/live
```
If PASS, add a timer or cron entry running the same command every 3 hours (one process at a time, memory cap 200M). Keep it running for 10 weeks. Data is about 2 MB a day.

## Report
1. Daily at 00:40Z commit `/root/charts/live/*` to `rn1/charts/live/` on the default branch.
2. First run: `agent/status/chart-recorder.md` (PASS/FAIL, last 20 lines) and `agent/outbox/2026-11-10-chart-recorder.md`.
3. The thread does the analysis. Raw data is never deleted before it is committed.
