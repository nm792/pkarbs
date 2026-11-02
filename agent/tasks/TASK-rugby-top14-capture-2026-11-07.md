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
- AB (merged, coordinator + Nick approval 2 Nov 15:50Z): 7 Nov, 13:15-18:05 UTC, ONE process, 6 matches (RC Vannes v Bordeaux 13:30 UTC per gamma; Toulouse v Clermont, 13:30 UTC per Rugbyrama 61242 and 15:35 UTC per gamma; Castres v Racing 92, Montpellier v Lyon, Pau v Perpignan, Toulon v Stade Francais at 15:35 UTC). Toulouse v Clermont is one entry, not two. Runtime limit 5 h (18000 s). Run with nice -n 19 and the same memory cap. Poll intervals unchanged. 36 tokens.
- D: 8 Nov, 13:45-16:30 UTC. 1 match: Vannes v Bordeaux at 14:00 UTC per Rugbyrama 61243 (Sun 8 Nov 15:00 Paris). 6 tokens.
- C: 8 Nov, 19:50-22:35 UTC. 1 match (La Rochelle v Bayonne, kickoff 20:05 UTC). 6 tokens.
Each window is at most 2 h 45 min. Do not start a window until the previous one is reviewed and its processes are gone.

## Procedure
```
systemd-run --scope -p MemoryMax=600M -p MemorySwapMax=0 nice -n 19 timeout 18000 python3 -u capture.py --window AB
```
capture.py: Python with `websockets` (or stdlib) only. Four concurrent async tasks in ONE process: (a) sports WS reader, (b) CLOB WS reader with reconnect at most 3 times, (c) poll loop for ESPN every 30 s and trades every 10 s, (d) Rugbyrama widget poll every 15 s (per 'Added 2 Nov 2026'). Append JSON lines to scratch files `rugby/<window>_sports.jsonl`, `rugby/<window>_clob.jsonl`, `rugby/<window>_espn.jsonl`, `rugby/<window>_trades.jsonl`, and a `rugby/<window>_log.txt` with connection events, reconnects and HTTP status counts. Stop at the window end time.

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

## Added 2 Nov 2026 (Nick approved, 15:44Z): Rugbyrama widget poll as an extra score clock
Purpose: record when each score event first appears on the Rugbyrama match widget. It is a first-seen clock, not a broadcast time. First test: does the widget update live during a match? If it never changes during play, say so in the report. Nothing else in this task depends on it.

- Endpoint (GET, honest User-Agent `pkarbs-research/1.0 (contact nm@delphic.co)`): `https://www.rugbyrama.fr/idalgo/cache/page/rugby_widget_match.php?refMatch=<id>`
- Poll every 15 s while the match is between kickoff minus 30 min and full time plus 15 min. Run it inside capture.py as a fourth async task, in the same process and memory cap. Do not start a separate process.
- Store the raw HTML response with the local receive timestamp in `rugby/<window>_rugbyrama.jsonl` (one line per poll: time, refMatch, status, size, body). Parse the event list (game minute, event text, running score). An event's first-seen time is the first poll whose parsed list contains it. Log first-seen times in `rugby/<window>_rugbyrama_events.jsonl`.
- Match IDs (from rugbyrama.fr results pages, checked 2 Nov 2026). Kickoffs below are Paris time (CET, UTC+1):
  - 61242 Stade Toulousain v Clermont, Sat 7 Nov 14:30 Paris (13:30 UTC)
  - 61237 Castres v Racing 92, Sat 7 Nov 16:35 Paris (15:35 UTC)
  - 61239 Montpellier v Lyon, Sat 7 Nov 16:35 Paris (15:35 UTC)
  - 61240 Pau v Perpignan, Sat 7 Nov 16:35 Paris (15:35 UTC)
  - 61241 Toulon v Stade Français, Sat 7 Nov 16:35 Paris (15:35 UTC)
  - 61238 La Rochelle v Bayonne, Sun 8 Nov 21:05 Paris (20:05 UTC)
  - 61243 Vannes v Bordeaux-Bègles, Sun 8 Nov 15:00 Paris (14:00 UTC)
- Window times are now derived from Polymarket gamma startTime (2 Nov 16:00Z), with 15 min padding before and 2.5 h after kickoff. Both sources list the same 7 fixtures. They agree on kickoff time for 4 of the 5 matches at 15:35 UTC on 7 Nov, and disagree on the other two (below).
- UNRESOLVED CONFLICT (2 matches). Rugbyrama 61242 Toulouse v Clermont shows 14:30 Paris (13:30 UTC) on Sat 7 Nov; gamma shows 15:35 UTC. Rugbyrama 61243 Vannes v Bordeaux-Begles is on Sun 8 Nov 15:00 Paris (14:00 UTC); gamma has it on Sat 7 Nov 13:30 UTC. Approved 2 Nov 15:50Z: windows A and B are merged into window AB (see Windows).
Coordinator decision (2 Nov 15:47Z): cover both sources. Window A includes Toulouse v Clermont at 13:30 UTC, and window D covers Vannes v Bordeaux at 14:00 UTC on 8 Nov. Window B keeps Toulouse v Clermont at 15:35 UTC per gamma.
- OPEN OVERLAP: windows A (13:15-16:00 UTC, 7 Nov) and B (15:20-18:05 UTC, 7 Nov) overlap by 40 min. Protocol rule 2 forbids overlapping jobs, so they cannot run as written. The coordinator must choose: shorten A, or move B's start. Do not run A or B until this is resolved.
- Gamma start times must be re-checked on 6 Nov, because Polymarket often fixes them before kickoff.
- Failure rules: a poll that returns non-200 or a parse error is logged, not fatal. Three consecutive failures on one match mean that match's Rugbyrama clock is marked FAILED for the report. It does not fail the window's score/price gates.
- Pass/fail for this clock is separate: PASS if at least one event's first-seen time was recorded during play. FAIL if the widget was polled for the whole match and no event appeared (report which match). Any lag figure is "first-seen at a 15 s poll", never "broadcast latency".
- Copy the Rugbyrama files to /mnt/project-files/rugby/live-2026-11/ with the other outputs.
