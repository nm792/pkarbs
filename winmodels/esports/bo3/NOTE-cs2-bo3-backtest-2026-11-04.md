# CS2 rules on 241 past Polymarket matches, timed with bo3.gg rounds (4 Nov 2026)

Confidence 6/10 (timing method validated on 21 maps; fills ignore queue position; to-result ranges span zero).

## Data
- bo3.gg API (api.bo3.gg/api/v1): every past CS2 round (winner, score, round length in ns) and each map's start
  time. **No clock time per round, and no live round data in the REST API** (a live map shows no score until it ends).
- Polymarket: 2,096 closed CS2 events (Sep 1 - Nov 4), 1,128 linked to bo3.gg matches (team names + start time).
  Top 250 by volume pulled (760 markets, v2 trades, window match start -1 h to end +3 h); 241 matches / 485 map
  markets / 10,657 rounds passed checks. These are mostly IEM/ESL/BLAST tier-1 matches: ~3.7 per day, not 45.
- Raw: winmodels/raw/bo3/ (matches, games+rounds, links, gamma, trades). Scripts in this folder; outputs
  out_bo3bt*.json/txt.

## Timing method (how "true round time" is built)
- Round-end time = A + s x (cumulative round length). On 32 maps also seen by our Polymarket WS logger this fits with
  ~5 s median error once A and s are fitted per map (s 1.03-1.09); the rest is the WS 20 s update grid.
- For the 241 matches, A and s are fitted per map to the Polymarket price: the values that centre the model-signed
  price move on the round ends. So **lag 0 = middle of the market's own reaction to the round**.
- Independent check: on 21 overlap maps, the WS logger receives each round a median **+19 s** after that point
  (p10-p90 +5 to +41 s). Matches the earlier 15-20 s WS delay estimate.
- Look-ahead guard ("cross-fit"): fit A, s on odd rounds only and trade only even rounds. Results below use this
  where it matters (lags <= +10 s overlap the fitting window in the plain run).

## 1. Event-only rule (bid mid x 0.975, maker only, 30 s window after a round, side the model says should rise >= 1c
## but hasn't, corrected fills, hold to result; beta fitted on first 120 matches, holdout = 121 from 16 Oct)
1-min edge (incl. rebate) by feed timing, all 241 matches, cross-fit (half the rounds):
| lag vs market reaction | -10 s | -5 s | 0 | +5 s | +10 s | +20 s (~WS) | +30 s |
|---|---|---|---|---|---|---|---|
| 1-min edge, cap 100 | +6.8% | +5.4% | +5.6% | +5.2% | +5.4% | +4.9% | +4.2% |
| 1-min edge, cap 500 | +6.6% | +5.3% | +5.4% | +5.3% | +5.2% | +4.6% | +3.9% |
| $/match to result, cap 100 | +$3 | +$4 | +$3 | +$2 | +$6 | +$9 | +$2 |
| $/match to result, cap 500 | +$6 | +$8 | -$1 | +$1 | +$10 | +$16 | -$1 |
- 90% ranges for $/match to result: about +/-$10 (cap 100) and +/-$35 (cap 500) at every lag. Holdout-only rows
  are -$26 to +$6 per match: no sign of a to-result profit.
- Plain run (all rounds, slight look-ahead at lags <= +10): $/fill per match $170 (cap 100) / $450 (cap 500);
  1-min edge +6.4% at 0, +3.2% at +20 s, +1.6% at +30 s; to result +$7 to +$11 per match (cap 100), ranges
  -$4 to +$22.
- Reading: the rule's fills do move our way over the next minute (~+5%, range +3 to +7%, holds in holdout), and the
  edge is almost as large at the WS's +20 s as at market time. Feed speed is not what limits it. Volume is:
  ~$170-450 filled per match, so the 1-min edge is worth ~$8-22 per tier-1 match, and to result we cannot tell it
  from zero yet.

## 2. rn1 resting pattern (bids at mid x 0.975 both sides through play, pulled 30 s after each round, + rebate)
| pull timing | -10 s | 0 | +10 s | +20 s (~WS) | +30 s |
|---|---|---|---|---|---|
| 1-min edge, cap 100 | -0.38% | -0.74% | -0.82% | -0.78% | -0.76% |
| $/match to result, cap 100 (all 241) | -$30 | -$35 | -$48 | -$29 | -$37 |
| $/match to result, cap 500 (all 241) | -$77 | -$87 | -$134 | -$78 | -$91 |
- $3.2-4.4k filled per match at cap 100. Holdout half is +$5 to +$39/match (cap 100), all-241 is -$29 to -$48:
  ranges span zero (about +/-$70 cap 100). The 1-min edge is negative at every pull time, even 10 s before the market.
- Reading: plain resting bids lose ~0.4-0.8% in the first minute on tier-1 CS2 even with a feed faster than the
  market. The losses come from in-round moves (kills, plants) that a round-end feed cannot see, not from slow pulls.
  rn1 makes its thin margin some other way here (queue priority, price levels, or market choice); copying the
  pattern without a filter does not pay on these 241 matches.

## Money
- Tier-1 matches like these: ~3.7/day. Event-only at ~$8-22/match = **~$30-80/day** (1-min edge basis, estimate).
- At 45 matches/day the same per-match value would be $360-1,000/day, but lower-tier books are thinner and were not
  tested; treat that as a ceiling, not a forecast. Queue position is ignored (fills optimistic).

## Fast feed (task b)
- bo3.gg REST: no live round scores (live map shows nothing until it ends). Its live channel would be on hosts we
  cannot reach (bo3.gg site and subdomains blocked at the proxy). Sofascore 403, HLTV blocked, GRID paid.
- No feed faster than the Polymarket WS (+19 s) is reachable today. Given section 1, a faster feed adds about one
  point of 1-min edge on a small fill volume, so it is not the main lever for CS2.
