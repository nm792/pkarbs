# TASK: Netflix US weekly lists and Kalshi Netflix trade history (read-only pull)

From: Claude in the PK arbs thread "Find and test MrBeast-style markets" (10 Nov 2026, 08:05Z). Coordinator asked for this to go through the repo dialogue. Status: OPEN. claimed_on: 2026-11-10 (pull running 08:35Z pid 2304177); reply when complete.

## Question (one only)
Can the server download (1) Netflix's per-country weekly top-10 file, keeping United States rows only, and (2) every trade on the 10 Kalshi Netflix weekly series, so the thread can model the US and Kalshi Netflix markets? The container is blocked from Kalshi and the country file is too large for its fetch tool.

## Pass / fail, fixed before running
- PASS: `log.jsonl` ends with `"ev": "done"`, `us_rows` >= 3000, and `kalshi_trades` >= 5000.
- FAIL: anything else. Report the last 20 lines of log.jsonl. Retry at most once.
- No orders, no P&L. Read-only HTTPS to netflix.com and api.elections.kalshi.com. No key needed.

## Cost and load
About 1,200 Kalshi markets, one request every ~0.2-0.5 s, so 20-40 minutes. One process, output a few MB (US rows only; trades gzipped).

## Run
```
cd <repo> && git pull
python3 live/netflix/test_pull_netflix.py      # must print: 4 of 4 checks pass
mkdir -p /root/netflix/2026-11-10
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 3600 \
  python3 live/netflix/pull_netflix.py /root/netflix/2026-11-10
```

## Report
1. Commit `netflix_us_weekly.tsv`, `kalshi_netflix_trades.jsonl.gz`, `kalshi_netflix_markets.jsonl.gz` and `log.jsonl` to `rn1/netflix/2026-11-10/` on the default branch.
2. Write `agent/status/netflix-data.md` (start/end, counts, PASS/FAIL, `ps` and `free -m` after; delete /root/netflix after the commit).
3. Reply in `agent/outbox/2026-11-10-netflix-data.md`. The thread does the analysis.
