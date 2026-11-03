# CS2 / Dota 2 live score feeds (3 Nov 2026, 06:55Z)

- Polymarket sports WS (wss://sports-api.polymarket.com/ws): one stream, no channels or subscriptions; every league comes in the same message type. Raw capture 05:46-06:11Z (raw/wscap/): CS2 TYLOO v 9z and a second CS2 match sent a 20 s heartbeat with round score 000-000 for 24 min (no round data). Dota 2: one message every ~120 s, map results only.
- 2 Nov server log (rn1/scores/cs2/live): tier-1 matches (Legacy v TheMongolz, Aurora v Liquid, PARIVISION v G2) DID carry round scores, 75 changes; signed lag vs price median +0.4 s, price first 47%. So round data depends on the match (tier-1 yes, tier-2 not seen). The logger already records every message; no logger change helps.
- Reconciled: "+0.4 s median" (2 Nov) and "~60% of the 1-min move happens before receipt" (3 Nov) say the same thing: feed and price arrive together, so the event-only rule gets no head start. CS2 event sim at lag 0 (event_sim.py): +0.8-1.6% at 1 min on $150-450 filled over 2-3 games, negative to result. Too small to judge.
- Other free sources tested from this container:
  - OpenDota /api/live: works, but every game carries delay=120 s (Steam spectator delay). Slower than price.
  - Steam Web API (GetLiveLeagueGames): blocked by proxy; needs a key; same spectator delay.
  - HLTV scorebot: 403 (Cloudflare). bo3.gg API and Liquipedia: blocked by proxy. GRID: paid (403). PandaScore free tier: no rounds.
- Result: no free CS2/Dota 2 feed is faster than the price. CS2 tier-1 round data from the PM WS is usable for measuring, not for a speed edge.

## CS2 event-only rule, LoL style (cs2_event_only.py, out_cs2_event_only.txt), 07:10Z
- Data: CS2 games 2-3 Nov with Polymarket round scores in our logs AND match-winner trades: 6 (Legacy-TheMongolz, MOUZ-TYLOO, Aurora-Liquid, PARIVISION-G2, megoshort-Falcons Force, Liquid-PARIVISION). Round data reached us for 7 of the 16 CS2 games the logger saw live; it is intermittent, not tier-based (NaVi-Falcons and FURIA-FaZe had none).
- Model: rounds to 13, Bo3 maps, map strength from the pre-match price. Jump fit beta 0.07 (R2 0.04, 246 rounds): one round moves the price far less than a simple model says.
- Rule (bid mkt x 0.975 on the side that should rise >= 1c but hasn't, 30 s window, corrected fills): filled $124-343 in total over 3-5 games across variants. 1-min edge -0.8% to +1.6%; lost to result in every variant. Far too thin to judge either way.
- Games needed: ~100 with round data (the LoL holdout was 93-174). At ~45% round coverage: PGL Major Singapore 25 Nov-13 Dec (~100 matches) gives ~45; BLAST Rivals 10-11 Nov a few more; reaching ~100 needs the Jan events (BLAST Bounty 11-24 Jan, IEM Krakow 27 Jan-7 Feb).

## Capture 2 (06:50-07:45Z, raw/wscap/ws_raw_20261103T0650Z.jsonl)
- FaZe v Team Falcons: round scores came through (17 changes, map 1 to 3-12). MOUZ v BetBoom: 55 min of 20 s heartbeats, no round scores. Dota 2 Direborn v Yangon Galacticos: 120 s cadence, no changes. Confirms round data is intermittent even for tier-1.
- Round changes land on the 20 s heartbeat grid (gaps 40, 80, 120 s...), so a round can reach us up to ~20 s after it ends, even though the 2 Nov median vs price was +0.4 s.
