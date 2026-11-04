# CS2 kill-level data via betting sites (4 Nov 2026)

Question: can a sportsbook (cross.bet first) give us CS2 data that moves on kills, ahead of the Polymarket price?
Raw probe: raw/bookmaker-probe-2026-11-04/probe.txt (10:40Z, from the Claude cloud container, US egress).

## 1. cross.bet (measured: blocked; in-play ruled out by law, 8/10)
- cross.bet and www.cross.bet now pass our network allowlist, but the site's own Cloudflare firewall refuses us
  ("Sorry, you have been blocked", HTTP 403) for plain curl AND a real headless Chrome. api.cross.bet is not allowlisted (502).
  Saved block page: raw/bookmaker-probe-2026-11-04/crossbet-cloudflare-block.html.
- CrossBet is an Australian racing/sports bookmaker (Cross Bet Holdings Pty Ltd, platform from BetMakers; expanding
  to Ontario). Australian law (Interactive Gambling Act 2001) bans online in-play sports betting by licensed books, so its
  site/app should not carry in-play CS2 odds at all. Its only use would be scores, which would be no faster than the
  round-score feeds we already have.
- Server test (non-US IP) requested from Hermes: agent/inbox/2026-11-04-crossbet-reachability.md. Timing run against
  IEM Beijing only if the server gets real pages back.

## 2. Bookmakers with in-play CS2 (desk research, 6/10)
- IEM / ESL Pro League official data is GRID-exclusive (ESL FACEIT Group deal from IEM Cologne 2025). Books that move
  IEM odds on kills either buy GRID (bet365 runs GRID's "CS2 Rushzone"; FeedConstruct/BetConstruct resells GRID) or
  watch the stream with their own traders (Pinnacle, Thunderpick, GG.bet, Stake, 1xBet, Betway, Cloudbet).
- An account is not what gives the speed: on almost all of these the live odds are visible without login. What blocks us is
  (a) our allowlist (every bookmaker host tested returns proxy 403), (b) their own bot firewalls, and (c) their terms.
- Terms (flag for Nick): bet365, Pinnacle, Stake, GG.bet, 1xBet, Betway and Thunderpick terms all forbid automated access /
  scraping of the site; breaches allow account closure and voiding bets. Not verified clause by clause yet.
- Allowed-for-bots routes: Betfair Exchange API (account + app key; live key is a one-off fee; in-play esports markets exist,
  CS2 liquidity thin), Smarkets public API (prices without login; esports coverage limited), odds aggregators with API keys
  (OddsPapi, odds-api.io: esports CS2, websocket, include Pinnacle; latency unknown). None tested: hosts not allowlisted.

## 3. Better lead: GRID itself, free tier (measured reachable, coverage unverified, 5/10)
- GRID's live API host api-op.grid.gg is now reachable from here: series-state and central-data GraphQL answer
  "UNAUTHENTICATED" (they want a key), so only a key is missing. (Earlier GRID 403s were the grid.gg website.)
- GRID Open Access (grid.gg/open-access) is a free application for developers covering a portion of official CS2 and Dota 2
  data. Series State = live per-player kills/round state, updated as actions occur. A third-party page says the free tier
  limits calls and excludes the Series Events stream. Which tournaments (IEM?) and any delay on the free tier: unverified.
- Next: Nick applies (a web form, no shell). If granted, Hermes installs the key on the server and we time Series State vs
  the PM book with capture.py. Domains to allowlist for the docs: grid.gg, docs.grid.gg, portal.grid.gg.

## Caveat carried from PR #63
At mid-2.5% about 2.7-3.7k shares already rest BEFORE the event, so kill-level speed alone may not fix zero fills;
any faster feed has to be re-checked against queue position at the price it lets us bid.

## 4. Owls Insight (11:00Z, from its official Python SDK on PyPI; site not allowlisted, 7/10)
Odds reseller, not game data. CS2 live = Pinnacle (and 1xBet) live odds relayed; CS2 history looks scoreboard-scraped.
Live Pinnacle stream needs MVP plan or above + WebSocket (Hall of Fame or add-on). Prices not seen. Useful only if
Pinnacle reprices mid-round on kills (unmeasured). Needs owlsinsight.com + api.owlsinsight.com allowlisted and a trial key.

## 5. LSports (11:20Z, public pages via search; lsports.eu not allowlisted, 5/10)
- B2B betting-data vendor (betting use is the product; sold to operators, expect company checks). Free trial advertised.
- Esports: odds + stats across ~21-23 titles; claims "0-1 s" in-play latency and "100+ live sources" (i.e. aggregated,
  not an official rights holder). Only CS item found is a 2022 CS:GO add-on; CS2 scope, kill-level events, and LoL/tennis
  depth not published. No public price.
- IEM data is GRID-exclusive, so LSports can be no faster than GRID-fed books or the stream for IEM. Tennis official
  fast data is Stats Perform (WTA) / Sportradar (ATP). Correction 11:30Z: Cito's ~11 s lead was vs PM's sports stream; vs the PM PRICE
  Cito points arrive a median 20 s AFTER the move (PR #68, 9 matches), and the tennis rule needs the point 5-10 s before.
- Break-even (USD, 30 days): $1,000/mo = $33/day, $3,000/mo = $100/day. Measured/simulated gains from more speed:
  LoL +$23/game (12 s -> 2 s, sim) = 1.5 games/day to cover $1k, 4-5/day for $3k, only until 14 Nov then none to mid Jan;
  CS2 not shown (queue, PR #63); tennis needs a 0-1 s point feed (Cito is ~20 s late vs price), gain not yet in $ (9 matches).
  LSports has no esports (Nick 11:23Z). For NBA (+$16-22/game sim, 5.5 s -> ~1 s, ~7 games/day) and tennis a free trial
  is worth taking; NBA only if the free NBA S3 test (night of 4-5 Nov) fails. NHL/cricket ~$0. Verdict: trial only, no paid plan yet.
