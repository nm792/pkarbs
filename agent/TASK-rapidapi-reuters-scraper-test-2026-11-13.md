# Task for the server agent: RapidAPI "Reuters API" scraper test

From: Claude in the "PK arbs" project, on Nick's instruction (13 Nov 2026). Status: OPEN. Deadline for Step 1 result: 45 min after you read this. Post status at the deadline even if unfinished.
Standard: feeds/STANDARD-feed-latency-test.md, VERSION 1 (cited, not restated). Benchmark = venue price (Polymarket NVDA-USD perp, Hyperliquid xyz:NVDA), never another feed.

## Hard rules
- Nick bought the RapidAPI PRO plan ($5/mo, 5,000 requests/month, listing says 5 req/s soft limit; check the exact limit on the plan page). Nick sends you the key directly. NEVER put it in Git, issues, notes or logs. Keep it in /etc/pkarbs/rapidapi.env (mode 600) as RAPIDAPI_KEY.
- Host: reuters-api.p.rapidapi.com. Headers: x-rapidapi-key, x-rapidapi-host: reuters-api.p.rapidapi.com. Endpoints: /latest, /search, /details, /category, /sections.
- Budget: 5,000 calls a month TOTAL. Plan the call count first and write it down. Do not exceed 4,000 in this test. No upgrade, no overage: stop when the budget is reached.
- Read-only. Data to /vol2 (charter). Commit only the small results notes.

## Step 1 (30 min): can it timestamp the NVDA resignation?
1. Call /search (and /latest, /details as needed) for the Nvidia / Jensen Huang resignation story of 12 Nov 2026. Record each call's HTTP status, response time, and the full publish/updated fields for the earliest matching article.
2. Compare the article's publish time with 13:48:14Z (first perp move; 8-K accepted 13:52:41Z). Write the difference. State plainly whether the timestamp field is first-publication or last-update, and whether it is to the second.
3. Write outbox/rapidapi-reuters-nvda-timestamp-2026-11-13.md. Verdict line: "Scraper carries a usable first-publication timestamp: yes / no".
If NO: stop, the scraper fails as a trigger. Do not buy anything.

## Step 2 (only if YES): poll lag, 30 min, then pre-registered test
- Poll /latest at a fixed interval (suggest every 15 s = 120 calls in 30 min; record exact receive time in ns, same host and chrony clock as the perp rows). For each article record first-seen receive time and its published time. Lag = first-seen minus published. Report median, p90, max.
- Compare a sample of 10 articles with the reuters.com timestamps on the public page, if the host is reachable from the server.
- If median lag is under 10 s, pre-register under STANDARD v1 in outbox/rapidapi-reuters-prereg-2026-11-13.md BEFORE reading results: events = headlines tagged to the symbols listed as perps on Polymarket/Hyperliquid, window [-60 s,+60 s], onset = first move >= 3 bp in the headline direction, 10 placebo times per event, n >= 30 events, median lead >= +2.0 s, bootstrap CI by event cluster excludes 0, price after feed >= 60%. Call budget must cover it; if not, say "unknown, settled by <when>".
- Independent audit (STANDARD v1 section 4) before anything is relayed.

## Notes
- The vendor says "real-time" but publishes no freshness figure. The 1.96 s on the listing is API response time only. Every claim here is from the author's reading of the vendor page.
- Nick does not SSH. Report only through outbox and status. Hermes silent since 02:54Z: IT has been told (see inbox/TO-IT-hermes-silent-new-tasks-2026-11-13.md).
