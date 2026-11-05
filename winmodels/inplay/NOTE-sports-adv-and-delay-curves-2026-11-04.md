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

### 4b. Rerun on the bigger Cito capture (15:30Z): race4 + cito-timing/tennis 10:55-15:20Z
- 118 Cito matches, 84 matched to Polymarket, 38 usable (37 had under 30 trades, mostly ITF; 5 unresolved). 8,015 point events.
- Model at price onset: predicted jump vs actual 30 s move beta 1.05, corr 0.75 (1,035 points with |jump| >= 2c).
- Cito arrives a median 27.5 s after the price starts to move (IQR 6.6-44 s).
- Delay curve (500 cap, W 30 s, min jump 1c, fixed in advance):
  - From Cito receipt, 0-10 s: $150-200 filled/match, 1 min ~0% (-0.1%, 90% -5 to +6%), result +10% but the 90% range is -29% to +67%. No edge.
  - From price onset (true-time proxy): -10 s $16/match, +14% at 1 min (90% 9-25%) = $2.2/match; 0 s $8/match, +7% (4-21%) = $0.6/match; 2-5 s $3-4/match.
- Verdict: the point model is right and the edge is real at the market's reaction time, but fills at market - 2.5% around the point are $8-16 per match, about $1-2 per match at 1 min even with a perfect feed. Cito is ~28 s too slow to get even that. Confidence 6/10.

### 4c. Full-day rerun (5 Nov 00:50Z): race4 + cito-timing/tennis 10:55Z 4 Nov - 00:xxZ 5 Nov
- Counts: 206 Cito matches; 161 matched to Polymarket; 56 had under 30 trades, 4 too few points, 2 unresolved -> 99 usable (161-56-4-2). 22,431 point events. (Earlier 38 = 84-37-4-5; the 4 and 5 were left out of my first message.)
- Model at price onset: beta 1.02, corr 0.74 (3,098 points). Cito arrives a median 26 s after the price starts to move (IQR 7-44 s).
- True-time (onset) delay curve, 500 cap, W 30 s: 0 s $7.8 filled/match, +12% at 1 min, held to result +12% (90% -43 to +49%) = $0.94/match; +5 s $5.6/match, result -18%; +10 s $6.0, +39%; +20 s $4.1, +20%; +30 s $5.9, -10%. All result ranges span zero.
- Longer bids (W 120 s, bid stays until the next point): $25-47 filled/match, held to result +46-62% (~$15-21/match) with 90% ranges above zero at 0, 5, 20, 30 s. BUT only 21 of 99 matches get any fill, and without the top 5 matches it loses (-12% to -42%). Not robust.
- By event type (onset 0 s, W 30): fills under $4/match for every type (break points $0.1, game points $3.7, holds $1.9, breaks/sets ~$0).
- Placebo (bid the opposite side): 10-15x more fills ($28k vs $0.8k), -3 to -7% at 1 min, ~0 to result. After a point, sellers dump the side that just lost; almost nobody sells the side that just won 2.5% under the market.
- Verdict: the model is right, but the 2.5%-under bid on the rising side almost never fills in tennis; the visible profit comes from about 5 matches. Best honest estimate ~$1/match (~$70/day at 70 matches), not distinguishable from zero. Confidence 6/10.

## 5. Tennis on historical matches, trade-only (5 Nov 01:20Z; tennis/hist/)
Nick: "why not just use historical matches?" No point feed exists for past matches (api.sofascore.com returns 403 to us), so events come from the trades.
- Data: gamma ATP + WTA singles moneylines starting 5 Oct - 2 Nov (2,010 events; raw/tennis/hist/). 1,895 usable (35 under 30 prints, 23 few in-play prints, 57 unresolved). 61 usable matches/day. 1.05M trades.
- Events: every mid move >= 2c within 20 s (one per 40 s), onset = first print covering 20% of the move (same definition as section 4). 76,811 moves, 41 per match.
- Side = direction of the move. That is oracle side choice, so returns are an upper bound (the point model gets the side right with corr 0.74, beta 1.0 at onset). Fills are a TRADE-BASED ESTIMATE: a print selling the rising side at most 1% under our bid (mid x 0.975) fills us, 500-share cap, queue ignored (optimistic).
- Check vs the 99 Cito-timed matches (CAL=1, 92 matched): this method gives $4.4 filled/match and $0.43/match at 0 s, against $7.8 and $0.94 from the point model. Same order, a bit lower.
- Delay curve, W 30 s (bid lives 30 s), held to result, per match with 90% range:
  - 5 s BEFORE onset: $17.6 filled, +22.5%, $3.97 ($1.6-6.6)
  - 0 s (instant of the market's move): $6.9 filled, +29%, $1.99 ($0.6-3.6); ex-top5 +12.8%
  - 2 s: $1.29 (-0.0 to 2.6); 5 s: $0.08 (-1.1 to 1.1); 10 s: -$0.63; 20 s: $0.42; 30 s: -$0.35
- W 120 s: 0 s $4.26/match ($0.7-7.8), 2 s $3.03 (-0.8 to 7.3), 5 s $1.68 (-2.6 to 6.1), 10 s and later negative (30 s -$8.8, range below zero).
- Verdict: confirms section 4c on 19x the matches. With a perfect zero-delay feed tennis is worth ~$2/match at W 30 (~$120/day at 61 ATP/WTA matches/day), up to ~$4/match at W 120 (~$260/day), and this is an upper bound (oracle side, no queue). By 5 s after the market starts to move it is ~0; every feed we have is 26 s+ behind the price. Tennis is not worth pursuing unless a feed reaches the point at or before the market's reaction. Confidence 7/10.
