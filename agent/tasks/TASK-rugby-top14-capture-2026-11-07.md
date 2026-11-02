# TASK: Top 14 live capture, 7-8 Nov 2026 (order books, trades, ESPN score timeline)

From: Claude in the PK arbs project thread "Size Polymarket rugby volume" (2 Nov 2026).
Requested by Nick. Status: OPEN, not started. Config: agent/tasks/rugby-top14-config-2026-11-07.json (windows A, B, C).

## Question (one only)
Across each Top 14 match's kickoff to full time, how many seconds after an ESPN score change does the Polymarket moneyline price move (measured on the book by 30 s REST polls and on trades)? Also: how much traded after kickoff versus before, per match?

## Pass / fail, fixed before running
- PASS for the capture: for each window, at least 95% of book polls, trade polls and ESPN polls succeed (no 429 or 403 storms), and no gap longer than 120 s in any match's trade or ESPN stream from kickoff minus 15 min to full time plus 10 min.
- FAIL: any window below that. Then report which window and which source failed, and do not report lag figures from it.
- No P&L. Lag figures are reported as a distribution with n events and the threshold used (2c move vs last trade before the score change).

## Windows (one bounded run each, one process at a time)
- A: 7 Nov, 13:15-15:45 UTC. 1 match (RC Vannes v Bordeaux, kickoff 13:30 UTC).
- B: 7 Nov, 15:20-18:00 UTC. 5 matches (kickoff 15:35 UTC each).
- C: 8 Nov, 19:50-22:30 UTC. 1 match (La Rochelle v Bayonne, kickoff 20:05 UTC).
Each window is at most 2 h 45 min. Do not start a window until the previous one is reviewed and its processes are gone.

## Sources (honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`)
- Book: `GET https://clob.polymarket.com/book?token_id=<yesToken>` for every market's yesToken in the config. Poll every 30 s. Store the raw JSON line per poll.
- Trades: `GET https://data-api.polymarket.com/trades?market=<conditionId>&limit=100`, every 30 s per market. Dedupe on transactionHash + timestamp + asset. Store new rows only.
- ESPN score: `GET https://site.api.espn.com/apis/site/v2/sports/rugby/270559/scoreboard`, every 30 s. Store the raw response for the two-team event(s) with competitions[0].status and score fields. Top 14 league ID 270559 (probe 2 Nov returned 200).
- Do not use the WS channel. It is not reachable from this sandbox.

## Procedure
```
UA='pkarbs-research/1.0 (contact nm@delphic.co)'
systemd-run --scope -p MemoryMax=600M -p MemorySwapMax=0 timeout 10500 python3 capture.py --window A
```
capture.py: stdlib only (urllib, json, time). One loop: for each poll cycle, fetch books, trades, ESPN, append JSON lines to scratch files `rugby/<window>_books.jsonl`, `rugby/<window>_trades.jsonl`, `rugby/<window>_espn.jsonl`, and a `rugby/<window>_log.txt` with HTTP status counts. Sleep to keep 30 s cycles. Stop at the window end time.

## Outputs
- Every 10 minutes, copy the three jsonl files and the log to /mnt/project-files/rugby/live-2026-11/ .
- At the end, commit the final copy under reports/rugby-capture/ in the repo.
- Post a status line in the thread about every 10 minutes during a window (status file agent/status/rugby-top14-capture.md).

## Cleanup (protocol rule 4)
Kill any process the window started. Remove scratch temp files. State `ps` and `free -m` output in the report.

## Labels (protocol rule 6)
Every figure is measured from the captured requests. Estimates are labelled as estimates. Lag figures are from ESPN timestamps, which may trail the broadcast, so do not call them broadcast latency.

## Known limits
- Book polls are every 30 s, not 1 s, so lag resolution from the book side is about 30 s. Trades are the better lag clock.
- ESPN scoreboard may trail the broadcast.
- Rugby markets are thin: most matches had $0 volume two days before kickoff, so some windows may show almost no trades. That is a result, not a failure.
