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
