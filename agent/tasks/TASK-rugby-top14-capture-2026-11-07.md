# TASK (v2): Top 14 live capture, 7-8 Nov 2026 (streamed books, trades, score feeds)

From: Claude in the PK arbs project thread "Size Polymarket rugby volume" (2 Nov 2026).
Requested by Nick. Status: OPEN, not started. Replaces the v1 polling task (PR #14, merged), which used 30 s polls and was too coarse: other price reactions in our data came 1-5 s after events.
Config: agent/tasks/rugby-top14-config-2026-11-07.json (windows A, B, C; both outcome tokens per market).

## Question (one only)
After each score change in a Top 14 match, how many seconds later does the Polymarket moneyline price move, measured on the streamed CLOB market channel?

## Pass / fail, fixed before running
- PASS for a window: the CLOB market stream is connected and delivering book or price_change messages for at least 90% of the window's minutes; no gap over 60 s in the score feed (sports WS rugby messages, or ESPN) from kickoff minus 15 min to full time plus 10 min; no 429 or 403 storm on the trade poll.
- FAIL for a window: any of the above not met. Then report which source failed and do not report lag figures from that window.
- If the CLOB stream refuses the connection (403 from the proxy, as seen from the sandbox on 2 Nov), that is a recorded result. Fall back to REST book polls every 5 s and label the lag figures "5 s poll resolution", not "stream". The fallback is not a failure of the task, but it must be stated in the report.
- No P&L. Lag figures are a distribution with n events and the threshold used (2c move vs the last trade before the score change).

## Sources (honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`)
1. **Score, primary: sports websocket** `wss://sports-api.polymarket.com/ws`. Hermes's logger keeps every sport from this channel. Filter messages where leagueAbbreviation is a Top 14 code (`rutopft`, from the config ticker prefix). Store each raw message with a local receive timestamp. Probe on 2 Nov over 200 s showed no rugby messages (only dota2, mlbb, challenger, atp, rus, cricket, cs2). That was an off-hours sample, so the result is inconclusive. The window must record whether any `rutopft` message arrived; if none did, the score clock is ESPN alone (say so in the report).
2. **Score, cross-check: ESPN** `GET https://site.api.espn.com/apis/site/v2/sports/rugby/270559/scoreboard` every 30 s. Top 14 league ID 270559 (2 Nov probe returned 200). Store the raw response for the event(s) with status and score.
3. **Prices, primary: CLOB market websocket** `wss://ws-subscriptions-clob.polymarket.com/ws/market`. Send `{"assets_ids": [<every clobTokenIds entry in the window's markets>], "type": "market"}`. Store every book, price_change and last_trade_price message raw, with local receive timestamp. Fallback if the connection is refused: REST `GET https://clob.polymarket.com/book?token_id=<yesToken>` every 5 s, one request per token, and the report says so.
4. **Trades: REST** `GET https://data-api.polymarket.com/trades?market=<conditionId>&limit=100` every 10 s per market. Dedupe on transactionHash + timestamp + asset. Store new rows only. This is the after-match audit clock.

## Windows (one bounded run each, one process at a time)
- A: 7 Nov, 13:15-15:45 UTC. 1 match (RC Vannes v Bordeaux, kickoff 13:30 UTC). 6 tokens.
- B: 7 Nov, 15:20-18:00 UTC. 5 matches (kickoff 15:35 UTC each). 30 tokens.
- C: 8 Nov, 19:50-22:30 UTC. 1 match (La Rochelle v Bayonne, kickoff 20:05 UTC). 6 tokens.
Each window is at most 2 h 45 min. Do not start a window until the previous one is reviewed and its processes are gone.

## Procedure
```
systemd-run --scope -p MemoryMax=600M -p MemorySwapMax=0 timeout 10500 python3 -u capture.py --window A
```
capture.py: Python with `websockets` (or stdlib) only. Three concurrent async tasks in ONE process: (a) sports WS reader, (b) CLOB WS reader with reconnect at most 3 times, (c) poll loop for ESPN every 30 s and trades every 10 s. Append JSON lines to scratch files `rugby/<window>_sports.jsonl`, `rugby/<window>_clob.jsonl`, `rugby/<window>_espn.jsonl`, `rugby/<window>_trades.jsonl`, and a `rugby/<window>_log.txt` with connection events, reconnects and HTTP status counts. Stop at the window end time.

## Outputs
- Every 10 minutes, copy the four jsonl files and the log to /mnt/project-files/rugby/live-2026-11/.
- At the end, commit the final copy under reports/rugby-capture/ in the repo.
- Post a status line in the thread about every 10 minutes during a window. Status file: agent/status/rugby-top14-capture.md.

## Cleanup (protocol rule 4)
Kill any process the window started. Remove scratch temp files. State `ps` and `free -m` output in the report.

## Labels (protocol rule 6)
Every figure is measured from captured messages. Estimates are labelled as estimates. ESPN and sports WS timestamps may trail the broadcast, so do not call the lag broadcast latency.

## Known limits
- Thin rugby markets: many matches had $0 volume two days before kickoff. Quiet windows are a result, not a failure.
- Whether the sports WS carries Top 14 at all is not yet known. The window report decides it.
- The CLOB WS was refused from the sandbox on 2 Nov (403). Whether it connects from the server is what the first window tests.
