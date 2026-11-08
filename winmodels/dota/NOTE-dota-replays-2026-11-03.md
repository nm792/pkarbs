# Replays for CS2 and Dota 2 history (3 Nov 2026, 08:15Z)

## CS2: not reachable
Demo and round-log sources all fail from this container: HLTV (demos and results) 403 Cloudflare; ESL, PGL, BLAST (site and API), FACEIT (open API), bo3.gg, GosuGamers, csstats, Twitch and YouTube are refused by the network allowlist; PandaScore free tier 403 on games/rounds. CS2 stays on the live capture route (PGL Major 25 Nov-13 Dec).

## Dota 2: works (OpenDota, free, allowed)
- **Matching (measured):** 1,858 closed Polymarket Dota 2 game-winner markets Jul-3 Nov 2026 (gamma series 10309); 1,280 matched to OpenDota pro matches by team names, time and game number; the winner agrees in 1,279 of 1,280.
- **Replay data:** OpenDota match detail gives every kill, tower, barracks, Roshan and teamfight with game-time seconds, plus gold advantage per minute (all 150 pulled were parsed). Pulled: top 150 games by volume (raw/dota/od, raw/dota/trades).
- **Alignment (game clock to wall clock):** start_time + game time + offset. Offset is not constant (median ~16 min: draft, pregame, broadcast delay), so it is fitted per game: (1) coarse, from the gold-advantage curve vs price level (median correlation 0.92); (2) refined to 1 s from signed price moves after events. Accuracy: split-half disagreement median 9 s (61% within 10 s, p90 93 s). 127 games aligned.
- **Leak control:** the refined offset uses the price, so the main test fits it on first-half events only and runs the rule only on second-half events. Train games before 1 Oct (jump betas: kill 2.6c, tower 1.3c, barracks 2.8c, Roshan 2.3c per net event; R2 0.20), holdout from 1 Oct.

## Event-only rule (LoL rule, corrected fills, Q cap, rebate), second-half events, 10 s window
| Set | Lag after market-aligned event | Games | $ filled | 1-min edge [90%] | To result incl. rebate [90% $] | Ex top 5 |
|---|---|---|---|---|---|---|
| Holdout | 0 s | 44 | $9.2k | +5.4% [+2.1, +9.3] | +22%, $2.1k [+0.8k, +3.3k] | +13.7% |
| Holdout | 5 s | 43 | $8.6k | +4.9% [+1.1, +9.1] | +18%, $1.6k [+0.3k, +2.7k] | +4.1% |
| All 98-108 | 0 s | 98 | $17.9k | +4.1% [+1.8, +6.6] | +15.5%, $2.8k [+0.9k, +4.5k] | +9.2% |
| All | 30 s (placebo) | 85 | $11.9k | -0.1% | +14.7% | +5.7% |
| All | 60 s (placebo) | 77 | $11.8k | -0.6% | +20% | +9.8% |
The 1-min edge is there at 0-10 s and gone by 30 s, as an event effect should be. The to-result figure stays positive even at 60-120 s, so part of it is not timing (the side that just won fights tends to win); treat the 1-min edge as the test.
Per game (holdout, 0-5 s): ~$200 filled, ~$35-50 net to result. Sim, first-in-queue; only 150 of 1,280 games pulled so far.

## What this does not settle
- **Live feed speed.** "Lag" here is measured from when the market reacted, not from a feed we can buy. Free live Dota data (OpenDota /api/live) carries a 120 s spectator delay; tournament broadcasts are also delayed. Whether our feed is ahead of or behind the market's broadcast is unmeasured: needs a live capture (poll OpenDota live every 5 s on pro games alongside prices) during the next tier-1 events (BLAST Slam 17-29 Nov, DreamLeague 2-13 Dec).
- Alignment error (median 9 s) blurs the 0-10 s lags.

## Update: all 1,280 matched games (out_event_only_oos_all.txt, out_placebo_all.txt)
- Alignment: 1,085 games aligned; split-half error median 12 s (44% within 10 s, p90 124 s). Betas (train 738 games): kill 2.5c, tower 1.2c, barracks 3.3c, Roshan 1.5c per net event.
- Leak-controlled (offset from first half, rule on second half), 10 s window:
| Set | Lag | Games | $ filled | 1-min [90%] | To result [90% $] | Ex top 5 |
|---|---|---|---|---|---|---|
| Holdout (from 1 Oct) | 0 s | 166 | $18.2k | +3.8% [+1.7, +6.0] | +16.7%, $3.1k [+1.4k, +4.7k] | +11.7% |
| Holdout | 5 s | 149 | $17.1k | +3.4% [+1.3, +5.8] | +14.3%, $2.4k [+1.0k, +3.9k] | +7.9% |
| Holdout | 10 s | 142 | $14.6k | +4.0% [+1.9, +6.0] | +12.7%, $1.9k [+0.4k, +3.5k] | +3.9% |
| All | 0 s, W30 | 650 | $100k | +3.5% [+2.6, +4.4] | +13.0%, $13.0k [+8.3k, +17.7k] | +10.0% |
- Lag sweep (all, W10): 1-min edge +4.3% (0 s), +2.4% (20 s), +1.2% (30 s), -0.6% (60 s), +0.4% (120 s). To-result stays ~+10-12% even at 60-300 s lag: the market under-reacts to events for minutes, so holding to the game result may pay even with OpenDota's 120 s-delayed live feed (lag 120: +10.8% to result, ex-top5 +7.6%, 333 games). Negative lags (bidding before the event) are lookahead, shown only as a check.
- Size (estimate): second-half-only results ~$15/game; whole game roughly double, ~$25-35/game. At October's ~18 Polymarket Dota games/day that is ~$450-600/day, before queue position and capacity limits. Sim, first-in-queue, 100-share cap per print.

## Live feed census (OpenDota /api/live, polled every 10 s, 13:45-15:42Z 3 Nov; raw: winmodels/raw/odlive_20261103.jsonl in shared folder)
- 9 league games seen, 2 leagues. EPL Masters 2026 (league 19944; OG v LEGION, CyberHero v Nemiga; Polymarket lists this league): delay 900 s. League 18631 (no team names): delay 10 s.
- OpenDota refreshes each live game about every 100 s (median gap between distinct last_update_time values), so the real lag is the delay plus ~50-100 s.
- So on EPL Masters the free live feed is ~16 min behind: useless. Need the census on tier-1 events (BLAST Slam 17-29 Nov, DreamLeague 2-13 Dec) before relying on it.
