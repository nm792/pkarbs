# Task for the server agent: timestamp the NVDA resignation headline with Massive (ex-Polygon) free trial

From: Claude in the "PK arbs" project, on Nick's instruction (13 Nov 2026). Status: OPEN. Post results by 07:00Z or say why not.

## Hard rules
- Nick gives the trial API key to YOU directly. Never write the key into Git, an issue, a note, a log or this repo. Keep it only in /etc/pkarbs/massive.env (mode 600) or an env var.
- Read-only market/news data. No orders, no accounts. Trial terms: stay inside them; if a call needs a paid plan, record the error text and move on.
- Data to /vol2/nvda-huang/ (charter). Commit only the small results note.

## Question
Perps (Polymarket NVDA-USD, Hyperliquid xyz:NVDA) first moved at 13:48:14Z on 12 Nov 2026 (mark 159.25 -> 156.13 by 13:48:40Z). The SEC 8-K was accepted at 13:52:41Z. What was the earliest published headline, and what did NVDA stock trade at in the same seconds?

## Pulls (window 2026-11-12 13:00Z to 15:00Z)
1. News, three sources, record published timestamp (UTC, full precision), source, title, and the time we fetched it:
   a. REST ticker news: GET https://api.massive.com/v2/reference/news?ticker=NVDA&published_utc.gte=2026-11-12T13:00:00Z&published_utc.lte=2026-11-12T15:00:00Z&order=asc&limit=1000  (docs: massive.com/docs/rest/stocks/news). NOTE: docs say this endpoint is updated HOURLY, so it may list articles late; record published_utc anyway and say how late each appears if you can tell.
   b. Benzinga partner news (massive.com/docs/rest/partners/benzinga/news), if the trial includes it: same window, NVDA. Record `published`, `updated`, and any headline-only items.
   c. Any news WebSocket channel the trial exposes (check massive.com/docs/websocket quickstart); if one exists, log it from now on to /vol2/nvda-huang/news_ws.jsonl.gz with local receive time.
2. NVDA trades, 13:40:00Z to 14:00:00Z: GET /v3/trades/NVDA?timestamp.gte=...&timestamp.lte=...&limit=50000 (nanosecond sip_timestamp and participant_timestamp). If the trial lacks tick history, use 1-second aggregates (/v2/aggs/ticker/NVDA/range/1/second/...) and say so.
3. Quotes (NBBO) for the same window if available.

## Output (outbox/massive-nvda-headline-2026-11-13.md)
- Earliest headline found: source, title, published timestamp (UTC), how many seconds before/after 13:48:14Z.
- NVDA trade price at 13:47:30, 13:48:00, 13:48:14, 13:48:40, 13:49:00, 13:52:41, 13:55:00 (last SIP trade at or before each time; note thin extended-hours trading).
- What the trial covers (news latency in practice, WebSocket channels, tick history depth, timestamp precision, rate limits, trial length and price after).
