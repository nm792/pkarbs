# Sports by ADV (total and in-play), plus NFL and tennis delay curves (4 Nov 2026)

Thread "Rank sports by in-play volume". Branch claude/project-thread-kg9dsj.

## 1. ADV ranking (measured)
- Window 20 Oct - 4 Nov 2026 (15 days). Gamma closed events in every /sports series: 230 leagues, $124.7M/day.
- In-play = volume after gameStartTime, from data-api v2 trades on sampled events (35-40 per league for the top 12, 10-12 for others), stratified by event size.
- Full table: ADV-2026-10-20_11-04.md (also /mnt/project-files/sports-volume/). Code: pull_events.py, inplay_share.py, adv_table.py. Raw: raw/inplay/.
- By sport, total (in-play) per day: soccer $35.1M ($19.2M); esports $29.1M ($24.8M); basketball $28.8M ($14.3M); tennis $14.5M ($13.1M); American football $12.5M ($7.6M); NHL $2.0M ($0.5M); MLB $1.3M; UFC $0.9M; cricket $0.5M.
- Caveat: only game events are counted. Outrights and futures are not in /sports series. Golf by tag over 12 months is $174M, of which the Masters 2026 Winner is $126M; 24% of it (top 12 markets) traded 9-13 Apr, about $6-7M/day in Masters week. Rugby is $3.1M per 12 months, Six Nations ~$1.4M. Raw: raw/golfrugby/.
- Gamma volume is about 2x v2 trade notional (size x price).

## 2. NFL delay curve (us/us_delay_hist.py, out_nfl_delay_hist_onset.json)
- Sample: 268 games, 2025 season. Train is Sep-Oct (121 games), test is Nov-Jan (147 games). Moneyline only, no rebates in 2025.
- ESPN play wallclock is not true event time: the price half-move lands a median 13 s before it (IQR -65 to +19 s). True event time is therefore proxied by price onset (first print at 20% of the move).
- Test, 500-share cap: $34-39 filled/game at 0-10 s. At 1 min +6-7% (~$2.5/game). Held to result +25-41% ($10-14/game), but the 90% range spans zero except at 10 s. The edge is gone by 20 s.
- Verdict: volume-limited, not feed-limited. About $5-25/day at 1.9 games/day.

## 3. Tennis first pass (tennis/tennis_delay.py, out_tennis_delay_onset.json)
- Sample: 144 ATP/WTA/Challenger matches, 2-4 Nov. Events are game and set changes from the server's PM sports-WS log. Event time is price onset.
- 0 s: +15% at 1 min, but only ~$3 filled/match. Flat or negative from 2 s.
- Why so few fills: the game winner is certain and their price jumps ~3c at once, so sellers rarely print 2.5% under the market.
- Server log snapshots (~30 s cadence) trail price onset by a median 37 s (games) and 27 s (sets).
- Stream push delay: NOT measured. The raw live capture (raw/tennis/ws_2026-11-04T0725Z.jsonl) stopped at 07:15Z when this idle cloud container was suspended (13 tennis messages, 3 matches). A capture has to run on the server or in an active session.
- Other thread (branch claude/project-thread-7f1y2j, live/cito_timing, 4 Nov 08:15-08:28Z): Cito's tennis WS (every point) gave game changes a median ~11 s before the PM stream (n=7, -9 to +26 s). Not yet timed against the price.
- Verdict: at true event time (price onset) the rule fills ~$3/match and is flat from 2 s, so a faster feed cannot fix it. The limit is fills, not the feed.

Confidence: ranking 8/10; NFL 6/10; tennis 5/10 (2 days, no serve information).

## 4. Tennis at point level (tennis/point/, out_point_delay.json), 4 Nov 11:00Z
Nick: reacting to game ends is reacting to what the market already priced. Redone on every point.
- Data: Cito tennis WS (every point, with server), recorded 08:14-09:10Z by the Cito thread (/mnt/project-files/cito-timing/race4). 32 Cito matches, 29 matched to Polymarket, 9 usable (12 had under 30 trades, mostly ITF; 6 not resolved yet). 846 point events.
- Model (tennis/point/tmodel.py): Markov point model (deuce, tiebreaks, sets, serve; doubles no-ad + match tiebreak). Serve-win probabilities re-fit before each point so the model equals the market mid; expected jump = model(new state) - mid.
- The model is right: from the price onset, the predicted jump vs the actual 30 s move gives beta 0.97, corr 0.73 (125 points with |jump| >= 2c).
- Cito is slow: Cito's message arrives a median 20.5 s AFTER the price starts moving (IQR 3 to 43 s). Measured from Cito receipt the model has no predictive value left (corr 0.05).
- Delay curve (500-share cap, W 30 s, min jump 1c, fixed in advance, no tuning):
  - From Cito receipt: 0-10 s $55 filled/match, +5.6% at 1 min ($3/match), 90% range spans zero; 20 s loses.
  - From price onset ("true" time proxy): 0, 2, 5, 10, 20 s -> zero fills. 5-10 s BEFORE onset -> $22 filled/match, +16% at 1 min ($3.5/match).
- Verdict: the edge only exists if we know the point before the market starts to react, i.e. courtside/official-data speed (seconds). Cito (scraped scores) is ~20 s too slow. Confidence 4/10: only 9 matches in 1 hour.
