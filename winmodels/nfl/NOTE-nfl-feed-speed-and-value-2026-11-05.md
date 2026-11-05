# NFL: feed speed vs the Polymarket price, and what the rule is worth (5 Nov 2026)

Thread "Measure NFL feed speed and value". Asked by Nick (5 Nov 03:16Z: "why are tennis and NFL not on the list?").
Rule: after a game event, bid market x 0.975 (rounded up to the tick, below the best ask) on the side that should rise; hold to result. Not market making.
Every delay below is measured against the Polymarket PRICE (when the market starts to move), not against the play.

## 1. Feed delays vs the price
### Polymarket sports WS (measured, 1 game)
- Monday 2 Nov CHI@SEA (3 Nov 01:15Z), frames from the server logger that kept every sports-WS message (rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz).
- NFL frames arrive on a fixed **5-minute cadence** (37 frames in 3 h 15 min; gaps 300 s, one 601 s, 902 s at half time). The same logger got CFB frames every 20-45 s, so this is the stream, not the logger.
- 9 scoring plays: the new score reached us a median **229 s after ESPN's play wallclock** (50 to 337 s) and **250 to 514 s after the price started moving** (8 with a clear move). ESPN wallclock itself is late for NFL (below), so the price-relative figure is the one that matters.
- Verdict: useless for the rule. It is 4-8 minutes behind the price.
### ESPN (historical only so far)
- ESPN's play wallclock is not true event time for NFL: the price half-move lands a median 17.5 s BEFORE it in 2026 (n 514, IQR -69 to +10 s) and 13 s before in 2025 (n 1,106). Live delivery delay of the ESPN API is not measured yet (NBA live test: 38 s after the event).
- Live capture tonight (JAX@BAL, 6 Nov 01:15Z): live/nfl_feeds/capture.py logs the sports WS, ESPN summary (1 s), ESPN scoreboard (1 s) and 1 s full order books.
### Other feeds
- From the cloud only ESPN and Polymarket are reachable. nfl.com/api.nfl.com, CBS, Yahoo, Fox, theScore, Sportradar and OddsPapi hosts are all blocked (curl, 5 Nov 03:20Z).
- NFL official data is sold through Genius Sports (company-only). Bookmaker prices (Pinnacle, bet365 via OddsPapi) are the only buyable route that could lead the PM price; not tested for NFL yet.

## 2. Backtests (Polymarket trade history, moneyline only)
### a) Score-change rule with the jump model (us/us_delay_hist.py, YEAR=26 EVT=onset)
- 2026 season to 3 Nov: 119 games (train 62 before 5 Oct, test 57). Event time = price onset. Parameters locked on train (W 20 s, min jump 2c, caught 0.5).
- Fills are tiny: $0-27/game filled at 500 cap. Held-to-result $/game swings from -$0.0 to +$9 with 90% ranges spanning zero, and every positive row is made by at most 5 games (ex-top-5 result -95% to -99%). **~$0/game.**
- Why: NFL prices move during the drive (yards, downs, red zone), so by the time the score posts the market has mostly moved.
### b) Upper bound on EVERY price move (nfl/hist_moves.py, same method as tennis/hist)
- Events = every mid move >= 2c within 20 s (any play), ~48 per game. ORACLE side, first in queue, fills on prints <= 1% under our bid, 500-share cap, bid lives 30 s, held to result.

| delay after price starts moving | 2026 (119 games) $/game held [90%] | 2025 (270 games) $/game held [90%] |
|---|---|---|
| 10 s BEFORE | +63.9 [28.0, 102.8] | +23.3 [-10.4, 67.1] |
| 5 s BEFORE | +35.5 [6.7, 66.5] | +3.3 [-14.2, 23.3] |
| 0 s | +7.6 [-9.7, 26.2] | +6.3 [-7.7, 22.9] |
| 2 s | +0.6 [-11.5, 13.3] | +4.6 [-9.2, 20.9] |
| 5 s | +1.3 [-12.2, 16.3] | +5.4 [-5.7, 18.9] |
| 10 s | -6.7 [-18.1, 3.8] | -0.7 [-11.3, 11.0] |
| 30 s | +3.0 [-23.2, 31.9] | +2.7 [-11.5, 16.6] |

- 1-minute markout at 0 s: +19% (2026) / +9% (2025) on $41-56 filled per game, gone by 10 s.
- With a 2-minute bid (W120) the 0-10 s rows are $8-15/game, all with ranges spanning zero.

## 3. $/game and $/day
- Games per day in season: 120 games in 55 days (10 Sep - 3 Nov 2026) = 2.2/day (mostly Sundays).
- Polymarket WS (4-8 min behind price): **$0/game, $0/day.**
- ESPN (to be measured tonight; historically its wallclock trails the price by ~15 s, NBA live delivery 38 s): at 10 s or later the upper bound is ~$0. **~$0/day** unless the live test shows ESPN ahead of the price.
- Perfect zero-delay feed: upper bound ~$6-8/game = **~$15/day**, not distinguishable from zero, before queue and with oracle side.
- Only a feed that knows the play 5-10 s BEFORE the price moves earns real money: ~$35-64/game on 2026 (~$80-140/day), $3-23/game on 2025. That is courtside/official-data speed.

## 4. Queue (1 s books)
- No historical books exist. The live capture tonight records 1 s books on JAX@BAL; Sunday 8 Nov (13 games) is the bigger sample. Queue can only lower the numbers above.

Confidence 7/10: WS cadence is from one game; ESPN live delay and queue are not measured yet; the move-based backtest is an upper bound.

Raw: raw/us_nfl26_hist (moneyline-only gamma events, trades), raw/us_hist26/nfl (ESPN), raw/nfl26 (CHI@SEA trades), raw/nfl26_espn_401873036.json.gz; full gamma pull in /mnt/project-files/nfl-feeds/raw/. Outputs: nfl/out_hist_moves.json, us/out_nfl26_delay_hist_onset.json.
