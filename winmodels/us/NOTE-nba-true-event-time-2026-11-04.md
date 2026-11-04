# NBA at true event time: delay curve and feed delays (4 Nov 2026)

Thread "Recheck NBA at true event time". Nick's 4 Nov rule: test the rule at true event time, then at +delays; measure our feed's delay; if the feed is too slow, find a faster one.

## What the 3 Nov test used
ESPN play `wallclock` (1 s). That timestamp is the NBA official `timeActual` cut to whole seconds (checked on LAC-TOR, 2 Nov), so it is true event time. The Polymarket price only starts moving at the timestamp: about 11% of the move comes before it, half within ~5 s, ~80% by 10 s (lag_nba.py, 6,992 score changes, 22 Oct-2 Nov). So the 3 Nov "lag 0" rows were already at true event time. The 3 Nov verdict rested on 39 held-out games, which is too few for a held-to-result result.

## Rule (unchanged)
After a score change, for W s: bid market x 0.975 (maker only, never at/above ask), only on the side the jump model says should rise >= 1c and hasn't yet. Fill only on taker prints within 1% below our bid (corrected fill rule). Held to result; rebates per market fee schedule (0 for 2025-26). Parameters were locked on train games (22-27 Oct 2026) at delay 0: W 10 s, min jump 1c, caught 1.0. Script nba_delay_curve.py. Assumes first in queue (optimistic).

## Delay curve, 429 out-of-sample games (2025-26 season, moneyline only; nba_delay_hist.py)

| delay after event | filled $/game (500 cap) | 1-min markout | held to result | $/game held (90% range of total) |
|---|---|---|---|---|
| 0 s | 206 | +8.3% | +19.3% | +39.8 (+$7.2k to +$27.1k) |
| 2 s | 151 | +8.8% | +21.8% | +32.9 (+$6.0k to +$22.1k) |
| 5 s | 98 | +6.2% | +17.9% | +17.5 (+$1.8k to +$13.1k) |
| 10 s | 63 | +2.5% | +13.9% | +8.7 (-$0.7k to +$8.1k) |
| 20 s | 102 | -1.1% | +8.2% | +8.3 (spans zero) |
| 30 s | 131 | -2.3% | -6.2% | -8.1 (spans zero) |
| 60 s | 129 | -2.3% | -1.5% | -2.0 (spans zero) |

At a 100-share cap: 0 s +$13.2/game, 2 s +$8.8, 5 s +$5.7, 10 s +$2.7. Excluding the top 5 games, the result stays positive at 0-5 s (+6% to +12%) and is gone by 10 s.

**Per day (sim):** ~7.2 regular-season games/day. At 500 cap: ~$290/day at 0 s, ~$240/day at 2 s, ~$125/day at 5 s, ~$60/day at 10 s, ~0 at 20 s or more.

2026 games (22 Oct-2 Nov, all markets, nba_delay_curve.py): the 1-min markout matches (+6.2% at 0 s, +2.5% at 5 s, ~0 at 20 s on 39 held-out games). Held to result it is -$42/game at 0 s (range -36% to +5%) on test and +$7.6/game on all 78 games. That is too few games to overturn the 429-game result, but it is a warning: this season's market may be sharper. The live check will tell.

Caveat: the margin-variance model (params.json) was fit on 2025-26 ESPN score paths, so the fair model has seen those games' scores but not their prices. Rule parameters and jump beta are from 2026 only.

## Feed delays (true event time -> us)
- Polymarket sports WS (Sportradar): median **5.5 s**, p10 3.0 s, p90 8.8 s (1,743 score changes, 15 games, 3 Nov; ws_vs_espn.py, server logger frames). That is worth ~$17/game (5 s row).
- ESPN summary API: not yet measured live (tonight).
- **NBA official liveData play-by-play** (S3 origin of cdn.nba.com, `nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/playbyplay/playbyplay_<gameId>.json`): free, reachable from the sandbox (cdn.nba.com itself is 403), with ms `timeActual`. Each action's last-edit time is a median 5.5 s after the event, 26% within 2 s. That is an upper bound on entry time; the live poll tonight measures it. If it arrives in ~2 s, it is worth ~$33/game.
- Live capture task: agent/tasks/nba-feed-delay.md (server, 5 Nov 23:50Z-06:45Z, 14 games). The PM WS side comes from the running cs2-ws-logger.

## Raw data
- /mnt/project-files/winmodels/raw/us_nba_hist_2025-26.tar.gz (432 gamma events, match, 432 moneyline trade files)
- /mnt/project-files/winmodels/raw/nba-liveData-2026-11-02/ (15 NBA play-by-play files + PM WS NBA frames 3 Nov)
- ESPN summaries: winmodels/raw/us_hist/nba (2025-26), winmodels/raw/us_bt/nba (2026)
- Outputs: out_nba_delay_curve.json, out_nba_delay_hist.json, out_ws_vs_espn.json

Confidence 7/10. The sign at 0-5 s is firm on 429 games. Size is optimistic because it assumes first in queue (LoL queue check suggests fills may be overstated), and the 2026 sample disagrees held to result.
