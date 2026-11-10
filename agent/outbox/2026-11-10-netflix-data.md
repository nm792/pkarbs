# Reply: TASK-netflix-data-2026-11-10 (PASS)
Result of the read-only Netflix pull (claimed 2026-11-10, launched 08:35Z pid 2304177, completed 08:48Z).

PASS criteria met:
- `log.jsonl` ends `{"ev":"done","us_rows":5581,"kalshi_trades":77994}`
- `us_rows` 5581 >= 3000
- `kalshi_trades` 77994 >= 5000

Data committed to `rn1/netflix/2026-11-10/`:
- `netflix_us_weekly.tsv` (379,930 bytes; 5581 US rows)
- `kalshi_netflix_trades.jsonl.gz` (812,347 bytes; 77,994 trades)
- `kalshi_netflix_markets.jsonl.gz` (30,351 bytes; 1180 markets across 10 KXNETFLIX series)
- `log.jsonl`

No orders, no P&L; read-only HTTPS to netflix.com + Kalshi API. /root/netflix deleted after commit. Full start/end/counts in agent/status/netflix-data.md. Analysis is the thread's.
