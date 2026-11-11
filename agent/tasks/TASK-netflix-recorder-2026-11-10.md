# TASK: record the free daily Netflix top 10 and the Polymarket Netflix books (every 30 min, 10 weeks)

From: Claude in the PK arbs thread "Find and test MrBeast-style markets" (10 Nov 2026, 09:00Z). Requested by Nick (free sources only, start recording now). Status: OPEN.

## Question (one only)
Does `live/netflix/record_netflix.py` run on the server and write both the daily Netflix top-10 lists (12 countries) and Polymarket Netflix order books?

## Pass / fail, fixed before running
- PASS after the first run: `wn_daily.jsonl` has 2 lines (yesterday and today), each with 12 countries; `books.jsonl.gz` has at least 20 rows; stdout ends with `"ev": "done"`.
- FAIL: anything else. Report the last 20 lines and stop. No retries beyond one.
- Read-only HTTPS to whats-on-netflix.com (robots.txt allows /most-popular/; one request per day, 3 s apart), gamma-api.polymarket.com and clob.polymarket.com. No keys, no orders.

## Run
```
cd <repo> && git pull
python3 live/netflix/test_record_netflix.py        # must print: 5 of 5 checks pass
mkdir -p /root/netflix/live
timeout 600 python3 live/netflix/record_netflix.py /root/netflix/live
```
If PASS, add a systemd timer or cron entry that runs the same command every 30 minutes (one process at a time, memory cap 300M, time limit 600 s). Keep it running for 10 weeks. Data is small (a few MB a day).

## Report
1. Daily at 00:30Z commit `/root/netflix/live/*` to `rn1/netflix/live/` on the default branch.
2. First run: `agent/status/netflix-recorder.md` (PASS/FAIL, ps/free -m) and `agent/outbox/2026-11-10-netflix-recorder.md`.
3. The thread does the analysis. Raw data is never deleted before it is committed.
