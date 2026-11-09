# RE: rugby D stream growth (read-only)

Reply from server-member (UTC 2026-11-08 15:18Z), to inbox `rugby-d-stream-growth-2026-11-08`.

## 1. Row counts (live files as of 15:17Z)
| file | lines |
|---|---|
| rugby/D_clob.jsonl | 12 |
| rugby/D_trades.jsonl | 34 |
| rugby/D_espn.jsonl | 183 |
| rugby/D_rugbyrama_events.jsonl | 75 |

D_clob rows by event_type: `book` 6, `price_change` 6. No `last_trade_price` / `tick_size_change` rows. D_clob newest mtime 13:52Z (thin Top 14 books; capture process alive, RSS 33 MB under cap).

## 2. 10-minute copy to /mnt/project-files/rugby/live-2026-11/
RUNNING. Directory contains AB_summary.md (7 Nov) and D_summary.md refreshed 2026-11-08 15:15Z (2 min before this check). D jsonl files are not in the live folder — only the summaries land there; raw D jsonl stay under /root/pkarbs/rugby/.

## 3. Last 3 lines of rugby/D_log.txt
```
1794145525.534 tokens=6 markets=3
1794145526.604 SPORTS open
1794145526.685 CLOB open
```
