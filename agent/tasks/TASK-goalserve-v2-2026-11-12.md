# TASK: Goalserve trial latency test v2 (SUPERSEDES TASK-goalserve-trial-2026-11-12.md and TASK-goalserve-odds-addendum-2026-11-12.md)

Why v2: Goalserve sent the real documentation and test feeds on 12 Nov. The earlier task assumed Pinnacle odds, WebSocket odds for esports and cricket, and event-level esports data. The docs say otherwise (see Facts). Test standard: feeds/STANDARD-feed-latency-test.md v1. Benchmark = Polymarket price only; other feeds are information only. Pass rules are NOT changed.

Start condition: /etc/pkarbs/goalserve.env exists with GOALSERVE_KEY, GOALSERVE_USER (login name emblematic07). NEVER write the key or the IP address into the repo, logs or status files. The vendor whitelisted one IP (in Nick's Goalserve email): confirm it equals this server's public egress IP before starting; if not, raise it to IT at once (agent/inbox, say "IP mismatch" only) and say so in status.

## Facts from the vendor docs (12 Nov)
- Live odds are **bet365 only** (vendor email: "live bet365 odds and live score via websocket"). There is NO Pinnacle in the in-play docs. Do not label anything Pinnacle.
- WebSocket sports: soccer, basket, tennis, baseball, amfootball, hockey, volleyball. NO esports, NO cricket, NO rugby on the WebSocket.
- Polled in-play odds files (gzip JSON, refresh 1 s, bet365): https://inplay.goalserve.com/inplay-{soccer,basket,tennis,volleyball,amfootball,esports,hockey,baseball}.gz. No cricket, no rugby.
- WebSocket: POST https://live.goalserve.com/api/v1/auth/gettoken, JSON body {"apiKey": KEY}, response {"token": JWT}; then connect wss://live.goalserve.com/ws/{sport}?tkn={token}. Static whitelisted IP required. Messages: mt="avl" (event list, bm, dt) and mt="updt" (odds update: id, mid, t1/t2 names, odds[] with v (price) and lv (last value), cms[] commentary events with tm, stats, pt = ms epoch of the update, uptd = update time string, sc, et, stp).
- Results by id: https://inplay.goalserve.com/results/{yyyyMM}/{id}.json. time_status: 0 not started, 1 in play, 2 to be fixed, 3 ended, 4 postponed, 5 cancelled, 6 walkover, 7 interrupted, 8 abandoned, 9 retired, 99 removed.
- Esports livescore REST (esports/home): refresh **every 1 minute**, score level (match/period score; CS2 map and round results with win type; per-map player stats). No kill, tower or Baron events for LoL/Dota. Useless for event latency. Esports in-play odds exist only as the polled 1 s file (plus a mapping feed esports/inplay-mapping).
- Tennis livescore REST (tennis_scores/home): refresh every 5 s; live point score in game_score (0/15/30/40/A) with serve; live point-by-point feed refreshes every 60 s.
- Cricket: cricket/livescore only; refresh period not stated. Rugby: rugby/home livescore only; refresh not stated. Hockey: hockey livescore + WebSocket + 1 s file.

## Signals to capture (one process, one clock, chrony-synced, data on /vol2 only; log local receive time ns, HTTP Date and vendor timestamps for information only)
1. TENNIS: (a) WS tennis updt stream; (b) inplay-tennis.gz polled every 0.5 s with ETag/Last-Modified; (c) tennis_scores/home polled every 1 s (point score). Events: point won (game_score change), bet365 moneyline implied-probability move >= 2c.
2. HOCKEY (NHL): (a) WS hockey; (b) inplay-hockey.gz at 0.5 s; (c) hockey livescore at 1 s. Events: goal, bet365 moneyline move >= 2c.
3. ESPORTS (LoL, CS2, Dota 2): inplay-esports.gz at 0.5 s only (bet365 live odds, 1 s refresh), plus esports/home at 5 s for score changes (information only, refresh is 60 s). Events: bet365 match/map winner price move >= 2c; map or round score change from the 1-minute feed (expect to lose).
4. CRICKET: cricket/livescore at 1 s. Events: ball, wicket, boundary. No odds available. Log the observed refresh interval of the feed (time between content changes) for the first week.
5. RUGBY: rugby/home at 1 s. Events: try, score change. Log observed refresh interval.
6. In parallel, existing recorders for Polymarket trades and books on the matched markets (and TheSports/ESPN/HLTV where they overlap, information only).

## Analysis (locked: STANDARD v1 sections 2-5; benchmark = PM price)
- Lead = PM price-move onset minus our receive time of the Goalserve message, placebo beside it, n shown. Poll resolution stated: 0.5 s polls on a 1 s file = +/-0.5 s; 1 s polls = +/-0.5 s on top of the vendor refresh; esports score = +/-30 s so it cannot pass.
- Odds signal event type (named before data): bet365 in-play moneyline implied probability moves >= 2c between consecutive updates. Lead = PM onset minus our receive of that update. Same bar: n>=30, median real-minus-placebo >= +2.0 s, bootstrap 95% CI by match excludes 0, PM moves after the Goalserve message in >=60% of events.
- Side comparison, information only: WS vs polled file arrival difference per event (tennis, hockey); Goalserve vs TheSports/ESPN/HLTV.
- Money bar if a sport passes: STANDARD section 5.
- Fewer than 30 events = unknown, settled by what and when.

## Deadlines
- Start within 1 h of the env file existing. Status in outbox/status every 30 min while blocked. If capture stalls, raise an IT issue immediately.
- Trial is 30 days from the vendor start date (not stated yet; ask). LoL final 14 Nov only if the env file exists by 13 Nov 12:00Z.
- Cricket/rugby verdict by 5 Dec using whatever live matches occur (BBL starts 12 Dec).
