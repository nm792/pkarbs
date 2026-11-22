# P98d — gas waiter live proof (22 Nov 2026)

- At 02:26Z the Nov 22 waiter had completed: `wait-20261122.log` records `LISTED after 1800 polls`, 5,097 polls with 0 errors, and 14 new trades with 0 errors.
- Books: 5,097 rows / 27,315,735 bytes; first/last receive times 2026-11-21 15:05:00Z–16:29:59Z. Trades: 14 rows / 12,607 bytes; first/last receive times 15:10:01Z–16:05:04Z. Both file sizes were unchanged across a 60-second recheck.
- PID 2259571 was absent. The requested `late_books_20261121.nohup` and expected `paper_books_late_2026-11-21.log` were absent; no late-books output was found.
- `crontab -l` showed daily capture at 07:35Z, waiter at 14:50Z and scorers at 16:10Z and 20:10Z. At 02:26Z, both 22 Nov book/trade files existed; the 22 Nov page log had not yet been created because its capture starts at 07:40Z. The scorer runs are therefore not yet verifiable.
- The 21 Nov page log contains 880 rows, all HTTP 403 (07:40:03Z–14:59:33Z). Its scorer output says `page_log_ok=false`, `days_scored=0`; this is not evidence about the 22 Nov run.
- Evidence remains on VOL2: `gas/us-gas-price-on-november-22-2026.{books,trades}.jsonl`, `gas/wait-20261122.log`, `gas/aaa_page_2026-11-21.jsonl`, and `gas/paper/paper_day_2026-11-21.log`.
