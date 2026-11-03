# CS2 / Dota 2 live score feeds (3 Nov 2026, 06:55Z)

- Polymarket sports WS (wss://sports-api.polymarket.com/ws): one stream, no channels or subscriptions; every league comes in the same message type. Raw capture 05:46-06:11Z (raw/wscap/): CS2 TYLOO v 9z and a second CS2 match sent a 20 s heartbeat with round score 000-000 for 24 min (no round data). Dota 2: one message every ~120 s, map results only.
- 2 Nov server log (rn1/scores/cs2/live): tier-1 matches (Legacy v TheMongolz, Aurora v Liquid, PARIVISION v G2) DID carry round scores, 75 changes; signed lag vs price median +0.4 s, price first 47%. So round data depends on the match (tier-1 yes, tier-2 not seen). The logger already records every message; no logger change helps.
- Reconciled: "+0.4 s median" (2 Nov) and "~60% of the 1-min move happens before receipt" (3 Nov) say the same thing: feed and price arrive together, so the event-only rule gets no head start. CS2 event sim at lag 0 (event_sim.py): +0.8-1.6% at 1 min on $150-450 filled over 2-3 games, negative to result. Too small to judge.
- Other free sources tested from this container:
  - OpenDota /api/live: works, but every game carries delay=120 s (Steam spectator delay). Slower than price.
  - Steam Web API (GetLiveLeagueGames): blocked by proxy; needs a key; same spectator delay.
  - HLTV scorebot: 403 (Cloudflare). bo3.gg API and Liquipedia: blocked by proxy. GRID: paid (403). PandaScore free tier: no rounds.
- Result: no free CS2/Dota 2 feed is faster than the price. CS2 tier-1 round data from the PM WS is usable for measuring, not for a speed edge.
