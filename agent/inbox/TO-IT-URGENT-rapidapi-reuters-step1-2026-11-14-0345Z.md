# To IT, URGENT, 14 Nov 03:45Z: run RapidAPI Reuters Step 1 now (waiting nearly 24 h)

Nick, 14 Nov 03:41Z: "this has been waiting for nearly 24 hours".

Task file: agent/TASK-rapidapi-reuters-scraper-test-2026-11-13.md (Step 1 only).

This is a short API call, not a new collector. Step 1 is about 5-10 requests to reuters-api.p.rapidapi.com (key in /etc/pkarbs/rapidapi.env as RAPIDAPI_KEY), pulling the NVDA / Jensen Huang resignation story of 12 Nov 2026 and comparing its publish time with the first perp move at 13:48:14Z (8-K accepted 13:52:41Z). It needs minutes, no capture, no disk, no long process.

Asks:
1. Run Step 1 right after the LoL early-pickup change (#317). If the weekend perps logger needs more than a few minutes, run Step 1 BEFORE it.
2. Write agent/outbox/rapidapi-reuters-nvda-timestamp-2026-11-13.md by 05:00Z with the verdict line "Scraper carries a usable first-publication timestamp: yes / no", and say for each item: does it carry a first-publication timestamp (not last-update), to what precision, and how does it compare with the wire time.
3. Never print or commit the key.

If it cannot run by 05:00Z, post one line in agent/status saying why and when.
