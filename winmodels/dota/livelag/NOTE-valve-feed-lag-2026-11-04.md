# Valve free Dota feed vs Polymarket: lag measured live, 4 Nov 2026

Thread "Time Valve's live Dota feed". Cloud capture 09:37-13:37Z (continuing), www.dota2.com allowlisted 4 Nov 05:48Z.

## Answer
In every Polymarket-listed Dota game we could time, Valve's free realtime feed (GetRealtimeStats) was **5 to 15 minutes behind the Polymarket price**. These delays match Valve's standard spectator-delay settings (300 s and 900 s), which the organiser chooses for each lobby. Using the lag-sweep table (>=180 s: -$0.3 per game, 0 edge), the feed is worth **$0 per day** for these leagues. Confidence 8/10 for the timed games, 6/10 for all Polymarket Dota leagues (5 games, 3 leagues).

## Game-end anchors (cleanest measure; all times are our receive times on one clock)
Valve "game over" = first realtime row with game_state 6. Market = the Game N winner book first showing bid >= 0.99 or ask <= 0.01. PM WS = Polymarket sports websocket map-score change.

| Game | League | Valve after price (s) | Valve after PM WS (s) |
|---|---|---|---|
| PuckChamp v Inner Circle G1 | Asgard | 300 | 247 |
| PuckChamp v Inner Circle G2 | Asgard | 296 | 248 |
| Yellow Submarine v NaVi G1 | EPL Masters | 981* | 858 |
| Yellow Submarine v NaVi G2 | EPL Masters | 920 | 859 |
| Xipto v Team Synapse G1 | Esports Pro Circuit | 899 | 586 |

*G1 price sat at ask 0.01 from 11:58:42Z, before the ancient fell. The PM WS column is the cleaner of the two.

Side finding: the Polymarket sports WS map score updates ~40-60 s after the price resolves (PuckChamp G1: price 0.99 at 11:09:23Z, WS 11:10:16Z).

## In-game check (cross-correlation)
30 s changes in the Valve net-worth lead and kill lead vs 30 s changes in the radiant price, lags -480..+120 s. Pooled peak at **L = -300 s** (the market moves 300 s before Valve shows it). PuckChamp G1 alone peaks at -285 s (r 0.55) against the series market. NaVi games can't be checked because 900 s is outside the search window, and their in-game correlation at short lags is ~0.

## Caveats
- The per-event half-move lag in lag.py (median 352 s, n=27) is a noisy estimate. Use the game-end anchors.
- The `delay_tag_s` field (GetLiveGames.time minus realtime game_time) is NOT a delay measure: GetLiveGames.time follows lobby time. Ignore it.
- LenS v Daxak G1 realtime stopped mid-game at 11:57:44Z (cause unknown), so it has no anchor.
- OG v GamerLegion (EPL) hadn't started by 13:32Z. The capture continues to 15:37Z.

## Files
- capture.js (cloud copy of agent/tasks/dota-live-capture/capture.js; PM-listed teams polled first, cap 12), config.json
- lag.py: pairing, cross-correlation, per-event lag, game-end anchors. out_lag.json / out_lag.txt
- raw-2026-11-04/*.jsonl.gz: Valve realtime + polls + league list, PM books, PM sports WS, OpenDota live, capture.log
