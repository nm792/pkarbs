# Faster CS2 score feed: options check (2 Nov 2026)

Question: is there a CS2 round-score feed that leads Polymarket's sports WS price move?
Current baseline (rn1/scores/cs2/live/NOTE-lag-2026-11-02.md): Polymarket sports WS score change lands about level with the price move (signed median +0.4 s, price first in 20 of 43 rounds).

## 1. HLTV live scorebot: NOT TESTED, blocked
- curl to https://www.hltv.org/ and /terms: CONNECT tunnel refused with 403 by the sandbox egress proxy (policy). WebFetch: DNS not resolvable (not on the allowlist).
- Terms of use could NOT be read from here. A WebSearch did not return HLTV's own terms page; results were third-party scrapers and vendor marketing only.
- Result: no terms verdict, no lag measurement. Two steps needed before any test: (a) Nick adds hltv.org to allowed domains and a NEW thread is started; (b) someone reads HLTV's terms and confirms automated access to the scorebot is allowed.

## 2. GRID (official, enterprise)
- grid.gg not reachable from the sandbox (DNS). Facts from search snippets only:
  - Open Access: free GRID API for pre-revenue startups, academics, independent developers and fans; covers CS2 and Dota 2 in-game data. Unclear from snippets whether it includes LIVE CS2 round events. Eligibility applies.
  - Live API / WebSocket: on the Media plan, pricing behind sales contact. Vendor claims sub-200 ms P95 for core CS2 live feeds (not independently verified).
- Next step if wanted: apply to Open Access (asks whether live CS2 round events are included), and request Media pricing. No purchase.

## 3. Bayes Esports (official, enterprise)
- Live Match Data: undelayed, high-granularity; supports CS, Dota 2, LoL; delivered over RabbitMQ.
- No free tier or trial found. Pricing "contact us". Free demo only.

## 4. Cito Esports API (third party)
- Free tier: 500 calls/month, 10 calls/min, live data on a 60-second delay. Too slow to lead the price; ruled out.

## 5. Tournament-organiser or other free official CS2 round feeds
- Not checked in this pass (no sources found in search). Polymarket's own sports WS is already the free official feed we use.

## Status
- Nothing paid, nothing signed up for. No paid feed approved (Nick's rule).
- No live capture was run: HLTV is blocked and the other official feeds are priced or unverified.

## Update 2 Nov 06:1xZ: trial options (Nick's question)
- grid.gg and docs.bayesesports.com: DNS-blocked from the sandbox. Facts below are from search snippets only, not from the pages.
- GRID Open Access: free for pre-revenue startups, academics, independent developers and fans. Snippets say CS2 and Dota 2 real-time match stats and in-game events are included; LoL live access not stated explicitly. Apply via the Open Access form (GRID contacts successful applicants). Hackathon-linked access has extra eligibility rules. Series Events is not included (paid). Usage limits apply. No trial period found. Delay for open access not stated. Betting/commercial-use limits not found.
- GRID LoL: separate "Get LoL data" form on grid.gg/get-lol.
- Bayes Esports: no free trial, sandbox or developer tier found. Access is via "Get in touch" on the Live Match Data page. Covers CS, Dota 2 and LoL (LoL access via Riot partnership; sales route). Delivery over RabbitMQ. Bayes Match Stats is a separate API, no trial stated.
- Nothing signed up for.

## Update 2 Nov 06:2xZ: GRID and Bayes terms, second pass (primary pages NOT read)
- Sandbox check: grid.gg returns 403 at CONNECT and docs.bayesesports.com returns 502 at CONNECT, even though Nick's note says both were added. This session still lacks the allowlist entries. www.grid.gg 307s to grid.gg. No primary GRID or Bayes page was read. Everything below is from search snippets.
- CORRECTION to the section above: "CS2 and Dota 2 real-time match stats and in-game events are included" is not supported by the newer search. GRID's own newsroom (grid.gg/resources/newsroom/what-is-grid-open-access/, snippet) says Open Access gives official HISTORICAL match data for select CS2 and Dota 2 tournaments. Live match data is for commercial partners. Treat live Open Access as NOT available until GRID confirms it.
- Eligibility (secondhand, unconfirmed): free for pre-revenue startups, academics, independent developers and fans (7wdata profile, Polymarket-bot listing). Not in GRID's own terms as read.
- Usage limits: a third-party listing says Open Access caps API calls and excludes Series Events. Not verified on grid.gg.
- LoL: the Polymarket-bot listing puts LoL in commercial tiers. A GRID hackathon terms page (last updated 3 Dec 2025, snippet) lists historical LoL and VALORANT data for one event. No standing LoL open-access terms found.
- Betting/trading use: a GRID hackathon data-terms snippet bars commercial use, copying, scraping, exporting and redistribution, and says data is accessed only through GRID APIs. A betting or trading product is commercial, so Open Access is very likely not usable for Polymarket trading. Snippet of the hackathon page only; standing Open Access terms not read. GRID's betting page lists a "Betting & Fantasy" tier as free with premium features, which conflicts with that clause. Needs a written answer from GRID.
- Access can be revoked, and the hackathon terms require deleting data at the end. Data licensing may depend on rights-holder partnerships (GRID's betting page says it is captured under official partnership with the rights holder).
- Delay: not stated in any source for Open Access. An old GRID help article (about 2022, snippet) says GRID data has no broadcast delay but gives no figure for API latency. Vendor claim of sub-200 ms P95 is unverified.
- Bayes Esports: no free trial, sandbox or developer tier found in search. Account creation is manual (they create accounts after contact). Access is sales-led. Bayes Match Stats and Live Data are paid products; the Fixtures API is for Live Data customers.
- Verdict for the free-feed question: no free LOW-COST live CS2 or LoL feed confirmed from GRID or Bayes. GRID Open Access is historical, unconfirmed for trading, and the terms probably bar trading use. Nothing signed up for; no paid feed approved.
- Confidence: 3/10 on the GRID terms (no primary text read). To reach 9, Nick needs to allow grid.gg and docs.bayesesports.com in a new session, or someone pastes the Open Access page and terms. Then re-read them and quote the exact clauses.
