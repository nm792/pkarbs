# Task for the server agent: live news-push feed test on the server (Massive first)

From: Claude in the "PK arbs" project, on Nick's instruction (13 Nov 2026). Status: OPEN.
Standard: feeds/STANDARD-feed-latency-test.md, VERSION 1 (cited, not restated). Benchmark = venue price (Polymarket NVDA-USD perp etc.), never another feed.

## Hard rules
- Nick gives the trial key to you directly. NEVER put it in Git, issues, notes or logs. Keep it in /etc/pkarbs/massive.env (mode 600).
- Read-only data. No orders, no accounts. Stay inside trial terms. Data to /vol2 (charter). Commit only the small results note.

## Step 1 (do now, 30 min): what does the trial actually push?
Without reading any results first, answer from the key itself, and write outbox/massive-news-capability-2026-11-13.md:
1. Does the trial include /benzinga/v2/news (docs: massive.com/docs/rest/partners/benzinga/news)? Call it once for NVDA; record the HTTP status and error text if refused.
2. Is there ANY push channel for news (WebSocket topic list in massive.com/docs/websocket, quickstart)? Connect and subscribe to what is offered. Record exactly what is pushed (news, or only trades/quotes/bars).
3. The regular /v2/reference/news is documented as updated HOURLY: record the lag between published_utc and the time it first appears (poll once a minute for 30 min).
Verdict line: "Massive provides a push news feed: yes / no". If NO: Massive fails as a news trigger; stop and say so. Do not buy anything.

## Step 2 (only if YES): latency test under STANDARD v1
- Pre-register BEFORE data is read, in outbox/massive-news-prereg-2026-11-13.md: event = a news item tagged NVDA/AAPL/TSLA/AMD/AVGO/MU/SPY etc. (the symbols Polymarket and Hyperliquid list as perps; use the 20 largest by volume), window [-60 s,+60 s], price-move onset = first mid move >= 2c-equivalent (use 3 bp) in the headline direction on Polymarket perp mark (1 s) and Hyperliquid mid, same-host receive timestamps (chrony), 10 placebo times per event.
- Log: WebSocket/stream messages with local receive time (ns), headline `published`/`updated`, perp mark/mids at 1 s. Run through at least two full US sessions.
- Pass per STANDARD v1 section 3 (n >= 30 events, median real-minus-placebo lead >= +2.0 s, bootstrap CI by event cluster excludes 0, price moves after the news in >= 60%). Fewer than 30 events = "unknown, settled by <when>".
- Independent audit before anything is relayed (STANDARD v1 section 4).

## Ranked vendor plan (13 Nov 05:10Z). Try in this order, stop at the first that pushes headlines live.
1. Massive Benzinga (Nick's trial key): Step 1 above decides yes/no in 30 min.
2. Alpaca news WebSocket (Benzinga-sourced, docs.alpaca.markets/us/docs/streaming-real-time-news): free paper account key, no card expected; verify on the vendor page when you sign up. Logger ready: weekend-perps/news_ws_logger.py (keys in env ALPACA_KEY/ALPACA_SECRET, never in Git). Needs Nick's OK to create an account in his name, so ask him via the repo inbox first.
3. Benzinga direct WebSocket (docs.benzinga.com/ws-reference/overview): trial by sales request; Nick or IT to request.
Latency measure for any of them: receive time (ns, same host as the perp price rows) minus the headline's published/created_at, plus the lead vs perp onset under STANDARD v1.
Reminder: practitioner threads (r/algotrading etc.) and vendor pages were blocked from the author's container; all vendor claims above are unverified search snippets.
