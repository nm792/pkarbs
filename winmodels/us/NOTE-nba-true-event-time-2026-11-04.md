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

## Live feed delays, 5 Nov 00:00-02:50Z (added 5 Nov 02:55Z; live_delay.py, sandbox poll of 10 games)
Every figure is measured against the NBA official `timeActual` (ms) of the play that set each new score.
- **Polymarket sports WS: median 5.8 s** (p10 3.6 s; n 24 on the same games tonight). This matches the 5.5 s from 3 Nov (n 1,743), so it is the fastest free feed.
- **NBA liveData S3 play-by-play: median 8.3 s** (p10 4.3, p25 6.0, p75 10.9; n 582 score changes, 10 games). The file is republished every ~8-22 s and reaches us ~0.2 s after its Last-Modified time. On the same scores it is a median 3.1 s behind the PM WS, and ahead of it only 25% of the time.
- **ESPN summary API: median 37.8 s** (p10 24.7, p90 56.4; n 610). Too slow. This is why its historical wallclock looks "true time" while its live delivery is not.
- Verdict: the best free feed is the PM sports WS at ~5.5 s, the 5 s row of the curve: **~+$17.5/game held, ~$125/day (sim, 500 cap, first in queue)**. The 0-2 s rows (+$33-40/game) need a sub-2 s feed. The only candidate is Sportradar/Genius direct (paid; Polymarket's own source), which is outside the no-paid-feeds rule.
- Raw: winmodels/raw/nbacap-2026-11-05-local/ (nba_actions, espn_plays, polls, pmws). The server capture (agent/status/nba-feed-delay.md) continues to 06:45Z.

## Update 5 Nov 07:30Z: delays vs the PRICE, queue, and tick-correct $/game (Nick's rules)
Scripts: price_vs_play.py, queue_check.py, mid_vs_book.py, nba_delay_hist_tick.py. Outputs: out_price_vs_play_*.json, out_queue_check.*, out_mid_vs_book.json, out_nba_delay_hist_tick.json.

**1. When does the price move after the official play (NBA `timeActual`)?** Trade-derived mid, 1 s, signed move after each score change:
| games | scores | 20% of the 60 s move | 50% | 80% |
|---|---|---|---|---|
| 3 Nov slate (15) | 1,359 | +3 s | +6 s | +16 s |
| 4-5 Nov slate (14) | 1,236 | +3 s | +7 s | +27 s |

**2. Each feed vs the price** (delay vs play = receipt minus `timeActual`; "vs price" = minus the +6/+7 s half-move time; negative = we hear it before the price is half-moved):
| feed | n | delay vs play | vs price half-move | move already done at receipt |
|---|---|---|---|---|
| Polymarket sports WS | 1,320 (3 Nov), 32 (4-5 Nov) | 5.0 s, 5.2 s | -1.0 s, -1.8 s | 38%, 46% |
| NBA liveData play-by-play (S3) | 1,109 | 7.8 s | +0.8 s | 42% |
| ESPN summary | 610 | 37.8 s | +31 s | ~100% |
(Earlier 5.5/5.8 s figures were against ESPN's whole-second wallclock; these use the NBA's ms time.) NBA is unlike CS2: the Polymarket stream arrives while the price is still moving, not after it. Caveat: price timing uses trade mids. In the only 1 s book window (5 min, late game, 31 events) the book mid moved slower (50% of the 30 s move at +16 s), so this needs the full-night books before I call it settled.

**3. Queue, from 5 min of 1 s books** (4 Nov slate, 22 tokens, 4,363 snapshots, all late-game; the sandbox was cut at 02:57Z): market tick is 0.001, spread median 1.0c; our bid at mid x 0.975 sits 0.6c below the best bid. Shares resting ahead of it: median 6,324 (12.6 clips of 500), p25 849, p75 67k, p90 206k. Only 26-37% of the time (mid 0.05-0.6) is it under 500 shares, 13% at mid 0.6-0.8, 0% above 0.8. Paper bids every 5 s: price traded through the bid within 30 s in 27% of cases (39% in 60 s), inflated because it is the late game. The sim's trade-mid differs from the book mid by a median 0.5c (p90 2.0c): its bid sat above the real best bid in 28% of snapshots (we would be first in line) and at or above the real best ask in 6.6% (a live post-only bid must skip those).

**4. $/game, queue-safe** (429 games of 2025-26, 500 cap, held to result; bid rounded down to the real 0.001 tick; fills only when a print trades strictly through our price, which fills us by price priority whatever the queue; at-level prints, which need the queue ahead consumed, are not counted):
| delay | $/game (net) | 90% range per game | $/day (7.2 games) |
|---|---|---|---|
| 0 s | +25.6 | +9.8 to +42.2 | ~$184 |
| 2 s | +20.2 | +7.6 to +32.2 | ~$145 |
| 5 s | +9.6 | -0.4 to +18.9 | ~$69 |
| 10 s | +2.9 | -7.4 to +12.7 | ~$21 |
| 20 s | +9.6 | -3.4 to +23.1 | noise |
| 30 s / 60 s | -6.4 / -4.7 | spans zero | negative |
100-share cap: +8.4, +5.7, +3.0, +0.2 per game at 0/2/5/10 s. **This corrects my earlier table** (+39.8/+32.9/+17.5 at 0/2/5 s), which used unrounded bids; rounding to the real tick removes prints at our own level. The Polymarket stream (5 s, 38-46% of the move already done) therefore earns ~$10/game (~$70/day); a feed under 2 s would earn ~$20 (~$145/day). Still sim: first in line for the trades-through path, trade-mid prices, ESPN-fitted margin model.

**5. Sub-2 s NBA feed, what it costs** (web search 5 Nov, vendor quotes private, treat as unverified): Sportradar NBA Push API (play-by-play over HTTP streaming) and its in-play incident feeds: no public price; third-party posts say custom contracts from about $10k/month for odds feeds. Genius Sports/BetGenius: no price found. SportsDataIO: partly self-serve, rest by sales. Goalserve lists "NBA/NCAA live data" at $250/month and claims max 1 s for in-play odds (not shown for NBA play-by-play). balldontlie All-Access listed at $499.99/month. None has a published NBA latency; ask for a measured one and a 1-week trial. Nick is asking vendors.

**6. Next:** agent/tasks/nba-books-ws.md asks the server for full-night 1 s books and the Polymarket WS NBA frames on 5-6 Nov, so queue and book-mid price timing can be done on 14 games instead of 5 minutes.

Confidence 6/10. Firm: the price takes ~6-7 s to half-move and the Polymarket stream beats that; the ranking of feeds. Not firm: the $ level (sim, trade-mid prices, no historical books) and the book-mid timing.
