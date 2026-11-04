# PandaScore live data for CS2 and LoL (4 Nov 2026)

Question (Nick, 11:00Z): why aren't we testing PandaScore on CS2 and LoL?
Short answer: nothing live is reachable on the free key, and there is no public live trial.
The only PandaScore product that could beat the Polymarket price is the **Low Latency Feed**, sold by quote only.

Sources read 4 Nov 11:00-11:20Z: pandascore.co/pricing, developers.pandascore.co plan-reference,
websockets-overview, sandbox-environment, low-latency-feed-overview, pandascore.co/predictions.

## The four products (mutually exclusive tiers + one separate feed)

| Product | Price (public) | Live data | Speed | Useful to us? |
|---|---|---|---|---|
| Free / Fixtures | 0 | None. Schedules, running-match list, results only. 1,000 req/h | n/a | No (already tested 2 Nov: match/game detail 403, rounds 404) |
| Historical | from EUR 400 /game/month | None live; post-game stats | n/a | No |
| Basic Live | from EUR 1,000 /game/month | Frames every ~2 s (CS: round score, kills, alive; LoL: kills, gold, towers, drakes, barons). No events feed | "Stream-synced": in sync with the public stream | No: stream data is what moves the PM price, so at best level with it. And the stats plans "are only available to customers with non betting-related usage" |
| Pro Live | contact sales | Frames + events (kills, round start/end, bomb) | Stream-synced | No, same reason |
| **Low Latency Feed** | contact sales@pandascore.co | CS2: round scores, player dead/alive, sides, bomb status, round timer, map. LoL: kills, game timer, draft, sides. Dota 2: timer, towers, gold lead, kills, draft | "Faster than the streams, in sync with our odds feed (the same data layer that moves betting lines)". Says Twitch/YouTube run 3-4 min behind. No number in seconds published | **Yes, the only candidate.** Built for "prediction bots, quant models". Internal use only |

- Free trial: none advertised for any live product. Sandbox (replays of past CS/LoL games) needs Basic Live or above.
- Data source: not stated. PandaScore calls it "expert-driven" and ties it to its own odds/trading team; it does
  not say GRID or official. Unknown.
- Network: api.pandascore.co is allowlisted, but live.pandascore.co (all websockets, including the low-latency one)
  is NOT reachable from our sandbox (curl 000). The server (Hermes) would run the capture anyway.

## What this means
- CS2 needs kill-level data before the price (price leads the round feed by ~44 s). The low-latency feed's
  "player dead/alive" is kill-level. LoL needs kills faster than our 12 s PM sports WS; the feed has kills.
- Nothing can be timed today (IEM Beijing, GEN at 22:00Z) without a low-latency key.
- Next step: ask PandaScore sales for a trial of the Low Latency Feed on CS2 + LoL, with a stated delay vs the
  game server, the data source, and price. If they give a key: Hermes installs it on the server, and we reuse
  live/cs2_feeds/capture.py + analyze.py against PM books (need live.pandascore.co allowlisted only if we capture here).

Confidence 8/10 (vendor docs, not measured; latency figure and price unknown until sales reply).
