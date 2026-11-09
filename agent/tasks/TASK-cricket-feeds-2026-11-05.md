# TASK: Cricket feed timing capture, 5 Nov 2026 (free feeds vs Polymarket price, for BBL 12 Dec)

From: Claude in the PK arbs thread "Time cricket feed for BBL" (5 Nov 2026, 01:15Z). Requested by Nick (plan item: BBL starts 12 Dec). Status: OPEN.

## Question (one only)
For every cricket match with a Polymarket market today, record the 1 s order book, the ESPN ball-by-ball feed (polled every 1 s) and the Polymarket sports-WS cricket messages, each with local receive ms, so the thread can measure how far each free feed lags the Polymarket PRICE on wickets and boundaries.

## Why on the server
The cloud container that started this capture is restarted whenever the thread goes idle (it died at 00:53Z). The server keeps running.

## Pass / fail, fixed before running
- PASS: the process runs from start to 17:15Z (or is stopped by the thread); books.jsonl and espn.jsonl both grow during 04:40-08:00Z (WBBL Strikers v Heat is live then); log.jsonl has no gap over 120 s without a books write while any market is live.
- FAIL: the process dies early or either file stops growing during WBBL play. Report which, with the last 20 lines of log.jsonl.
- No P&L, no orders. Read-only HTTP + one WS.

## Code (repo, merged on the default branch)
`live/cricket_feeds/capture.py`: one Python process (threads). It uses only websockets plus the standard library (requests is optional). It polls `clob.polymarket.com/books` about once a second for roughly 40-80 tokens, polls `site.api.espn.com` playbyplay every second for each live non-first-class match (2-5 at once), and makes one WS connection to `sports-api.polymarket.com/ws`. It copies jsonl to `--share` every 10 min and stops itself after HOURS.

```
cd <repo> && git pull
mkdir -p /root/cricket-feeds/2026-11-05
systemd-run --scope -p MemoryMax=500M -p MemorySwapMax=0 timeout 58000 \
  python3 live/cricket_feeds/capture.py /root/cricket-feeds/2026-11-05 15.9 \
  --share /root/cricket-feeds/2026-11-05/share
```
Start it as soon as you read this (the target window starts at 03:30Z). If you start after 03:30Z, still run it and note the start time.

## Report
1. Every hour, commit the files in `share/` (gzip books.jsonl first) to `rn1/scores/cricket/feeds-2026-11-05/` on the default branch. They are small, apart from books (~20-40 MB raw).
2. Write `agent/status/cricket-feeds.md` with the start time, rows per file, the pass/fail result, and `ps` / `free -m` output after it stops (cleanup).
3. Reply in `agent/outbox/2026-11-05-cricket-feeds.md`. The thread does the analysis.

## Protocol notes
- This is a light poller, about 4-7 requests a second in total, with a single process. It does not overlap any other open cricket task.
- Use an honest User-Agent (pkarbs-cricket-feeds). Do not work around any 403. ESPNcricinfo is Akamai-blocked from cloud IPs and is not polled.
