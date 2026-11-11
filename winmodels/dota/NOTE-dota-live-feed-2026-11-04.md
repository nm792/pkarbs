# Fast live Dota 2 feed (4 Nov 2026, thread "Find a fast live Dota 2 feed")

## Sources (tested 4 Nov 05:40-05:50Z)
| Source | Data | Delay | Price | Reachable |
|---|---|---|---|---|
| Valve www.dota2.com/webapi IDOTA2MatchStats/GetRealtimeStats (keyless) | per-player kills/deaths, net worth, levels, every tower/barracks, gold graph; refreshes every few s | spectator delay of the lobby (inferred: realtime game_time trails GetLiveGames clock by 105-177 s on 3 tier-3 games with 120 s delay); to measure vs price | free | blocked in sandbox (asked Nick to allowlist); works via TinyFish; server capture PR #43 |
| Valve IDOTA2League/GetLiveGames (keyless) | live league games, server_steam_id, game clock | clock looks ~live | free | as above |
| Steam Web API api.steampowered.com (GetTopLiveGame, GetRealtimeStats, GetLiveLeagueGames) | same as Valve rows | same | free key | 403 without key; blocked in sandbox |
| OpenDota /api/live | scores, gold lead | delay 120-900 s + ~100 s refresh (3 Nov census) | free | yes |
| Polymarket sports WS | Dota series: map score only ("000-000|1-0|Bo3"), kills 000-000 | ~120 s cadence (3 Nov) | free | yes |
| GRID | official BLAST (incl. BLAST Slam) and ESL FACEIT (DreamLeague) data, exclusive | low latency (vendor claim) | company clients only, fixed fee + revenue share; rejected by Nick 4 Nov | 403 |
| PandaScore | Dota live WS, tier 1 | ~0.3 s "from stream" (vendor claim, CS2/LoL) | rejected 2 Nov (EUR 400-1000/game/month) | 403 on free tier |
| Abios (via Bayes rights, Bayes insolvent), Oddin (B2B odds, uses GRID), LSports, Goalserve (~$5.1k package), Cito ($59/mo, source unknown) | odds/live data | unknown | quotes | not tested |
| STRATZ, Datdota, Dotabuff, Liquipedia, cyberscore, hawk.live, dltv | various | unknown | free/paid | blocked by sandbox proxy |

## Lag sweep (lag_sweep.py, out_lag_sweep.json): event-only rule, leak-controlled, second-half events, W30, holdout 344 games from 1 Oct
| Lag after market-aligned event | 1-min edge [90%] | To result incl. rebate, $ per listed game (second half) |
|---|---|---|
| 0 s | +3.3% [+1.6, +5.1] | $12.0 |
| 10 s | +2.5% [+0.9, +4.2] | $8.4 |
| 20 s | +1.8% [+0.3, +3.2] | $7.5 |
| 30 s | +2.0% [+0.1, +3.7] | $9.9 |
| 60 s | +1.8% [-0.1, +3.6] | $7.1 |
| 90 s | -0.6% | $0.2 |
| 120 s | -0.4% | $4.3 |
| 180 s | -2.3% | -$0.3 |
Sim on real trades, first-in-queue, 100-share cap. Whole game ~2x second half (estimate); ~18 Polymarket Dota games/day (October).

## Live measurement, 4 Nov (cloud capture, raw: /mnt/project-files/winmodels/raw/dotacap-cloud-2026-11-04/; thread "Time Valve's live Dota feed")
- PuckChamp v Inner Circle G1 (Asgard): Polymarket G1 price hit 0.99 at 11:09:23Z, PM sports WS 1-0 at 11:10:16Z (+53 s), Valve game_state 6 at 11:14:23Z (+300 s). Cross-correlation of net-worth/kill lead vs price peaks at -285 s.
- Yellow Submarine v NaVi G1 (EPL Masters): Polymarket G1 price moved 0.28 -> 0.62 between 11:24 and 11:37Z while Valve still showed pre-horn (horn at 11:35:55Z on Valve, 0-0 kills to 11:37). Consistent with OpenDota's 900 s delay tag on this league: Valve is roughly 10-15 min behind the market.
- So on today's Polymarket-listed leagues Valve's free feed is 300-900 s behind the price. Lag sweep at >= 180 s: about $0 per game. No edge from the free feed on these leagues.
- Caveat: GetLiveGames 'time' is lobby time (incl. draft), not a delay tag. Per-game delay = Valve game end vs price reaching 0.99.

## All Polymarket series on 4 Nov (server capture to 18:17Z, livelag/lag.py; out: livelag/out_lag_server_2026-11-04.json)
Valve game end (game_state 6) minus Polymarket game-winner price reaching 0.99, and minus PM sports WS map-score change:
| Game | League | Valve - price | Valve - PM WS |
|---|---|---|---|
| PuckChamp v Inner Circle G1 | Asgard | 299 s | 246 s |
| Zero Tenacity v angry birds G1 | Asgard | 298 s | 221 s |
| Zero Tenacity v angry birds G2 | Asgard | 301 s | 135 s |
| Spirit Academy v Xipto G1 | Asgard | 956 s | 677 s |
| Yellow Submarine v NaVi G1 | EPL Masters | 978 s | 857 s |
| OG v GamerLegion (series market) | EPL Masters | 1463 s | 860 s |
| CyberHero v HULIGANI G1 | EPL Masters | 1094 s | 772 s |
| Xipto v Synapse G1 (cloud capture) | Esports Pro Circuit | 899 s | 586 s |
In-game kill/tower events (23 timed): Valve median 346 s after the price (p10-p90 245-424 s). No Polymarket-listed game today had a short delay; Media Eleague games dropped out of Valve's feed mid-game. Verdict: free Valve feed is 5-16 min behind on every Polymarket Dota league seen; ~$0/game. Games after 18:17Z (Allied v Lynx, Cooman v Stray) not in the repo copy.
