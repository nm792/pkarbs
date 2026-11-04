# Fast live Dota 2 feed (4 Nov 2026, thread "Find a fast live Dota 2 feed")

## Sources (tested 4 Nov 05:40-05:50Z)
| Source | Data | Delay | Price | Reachable |
|---|---|---|---|---|
| Valve www.dota2.com/webapi IDOTA2MatchStats/GetRealtimeStats (keyless) | per-player kills/deaths, net worth, levels, every tower/barracks, gold graph; refreshes every few s | spectator delay of the lobby (inferred: realtime game_time trails GetLiveGames clock by 105-177 s on 3 tier-3 games with 120 s delay); to measure vs price | free | blocked in sandbox (asked Nick to allowlist); works via TinyFish; server capture PR #43 |
| Valve IDOTA2League/GetLiveGames (keyless) | live league games, server_steam_id, game clock | clock looks ~live | free | as above |
| Steam Web API api.steampowered.com (GetTopLiveGame, GetRealtimeStats, GetLiveLeagueGames) | same as Valve rows | same | free key | 403 without key; blocked in sandbox |
| OpenDota /api/live | scores, gold lead | delay 120-900 s + ~100 s refresh (3 Nov census) | free | yes |
| Polymarket sports WS | Dota series: map score only ("000-000|1-0|Bo3"), kills 000-000 | ~120 s cadence (3 Nov) | free | yes |
| GRID | official BLAST (incl. BLAST Slam) and ESL FACEIT (DreamLeague) data, exclusive | low latency (vendor claim) | quote only; Nick asked, no reply | 403 |
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
