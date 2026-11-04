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

---
# Follow-ups (4 Nov, later): rn1's CS2 fills, bigger size, smaller tournaments

All $ below are **net of an estimated maker rebate** (~0.3% of $ filled; makers pay no fee). Gross = net minus
"reb/m" in the out_*.json files: $0.3-1.4/match for event-only, $11-35/match for resting.
Span of the linked data is 43 days (Polymarket CS2 match events from ~22 Sep), so tier-1 = 241 matches = 5.6/day
(not 3.7/day as in section "Money" above), smaller tournaments = 558 matches = 13/day.

## A. When rn1 gets filled inside a CS2 round (rn1_phase.py, out_rn1_phase.json)
42 matches / 125 markets in rn1's 22-29 Oct data, $2.19M rn1 maker fills ($0.67M taker), gross 1-min +1.49%.
| seconds since round end | 0-10 | 10-20 | 20-30 | 30-45 | 45-60 | 60-90 | 90-120 | 120+ |
|---|---|---|---|---|---|---|---|---|
| rn1 share of traded $ | 17.7% | 15.5% | 15.9% | 16.1% | 15.9% | 15.1% | 14.8% | 7.9% |
| rn1 1-min markout | +1.4% | +1.9% | +0.8% | +1.5% | +1.8% | +1.5% | +1.5% | +1.5% |
Last 0-5 / 5-10 s before a round ends: share 12.2% / 12.4%, markout +1.2% / -1.3%.
- rn1 does not pull around round ends (largest share is right as the market reacts) and shows no mid-round pull.
  No sign of a feed faster than the market or of kill/plant data. 120+ s = timeouts and half-time (fewer of its bids).

## B. rn1's real fills vs our resting sim on the same 42 matches (rn1_vs_sim.py, out_rn1_vs_sim.json)
| | rn1 real (maker) | our sim (2.5% under, pulled 30 s, cap 100) |
|---|---|---|
| $ filled | $2.19M | $0.14M |
| distance under trade mid ($-wtd / median) | 2.0% / 1.4% | 2.5% / 2.5% |
| 1-min markout, gross | +1.49% | -1.14% |
| favourites (p>=0.5) | $1.35M, 0.8% under (median), +0.86% | -1.06% |
| underdogs | $0.84M, 2.3% under, +2.51% | -1.24% |
| map / match markets | +1.80% / +1.07% | -1.49% / -0.69% |
- rn1 sits about **1c under mid at every price level** (5.3% under at 0.1-0.3, 0.9% at 0.7-0.9), not a fixed %.
- 17% of rn1's maker $ fills **above** our trade-derived mid and still makes +1.1% at 1 min; its 5-15% deep fills
  make +3.6% to +6.7%. Profit rises with distance under mid.
- Our sim at rn1-like levels (rest_place.py, out_rest_place_rn1_42*.json): 0.5-2c under mid, or 4-15% under,
  with/without pulls, last- or first-in-queue fills: 1-min markout -0.8% to +1.4%, mostly negative, ranges span 0.
  **Placement level alone does not reproduce rn1.** What we cannot see: rn1's reference price. Its fills above our
  mid that still win mean it prices off something faster than the last trades (live order book, or outside odds),
  and it re-quotes off it. Queue priority and cancels are not in public data.
- Next test: record the live CLOB book (price_change WS) on today's CS2 matches, rebuild mid from the book, and
  rerun this comparison. If the book mid closes the gap, the fix is our reference price.

## C. Event-only rule: bigger caps, longer windows, smaller tournaments (bo3bt_grid.py, out_grid_*.json)
At our real feed timing (WS, +20 s), all rounds, net of rebate. $/match to result with 90% range; 1-min edge.
Tier-1 (241 matches, 5.6/day):
| window | cap 100 | cap 500 | cap 1,000 | cap 2,000 | no cap |
|---|---|---|---|---|---|
| 30 s | $7 [-3, 16], +3.5% | $18 [-11, 45], +3.8% | $24 [-22, 73], +3.8% | $47 [-22, 115], +3.6% | $73 [-103, 247], +2.2% |
| 60 s | $8 [-7, 22], +1.8% | $15 [-28, 60], +2.1% | $21 [-50, 94], +2.3% | $52 [-52, 157], +2.3% | $124 [-104, 351], +2.3% |
| 90 s | $13, +0.5% | $30, +0.9% | $49, +1.1% | $103 [-26, 232], +1.2% | $202, +1.4% |
Smaller tournaments (558 matches, 13/day; fills $38-300/match):
| window | cap 100 | cap 500 | cap 1,000 | no cap |
|---|---|---|---|---|
| 30 s | $4.7 [1.9, 7.8], +1.9% | $4.8 [-1, 11], +2.1% | $4.8 [-2, 13], +2.2% | $6.6 [-4, 18], +3.0% |
| 60 s | $8.0 [3.8, 12.6], +1.0% | $10 [2, 20], +0.8% | $12 [1, 24], +0.7% | $16 [2, 30], +0.9% |
| 90 s | $8.0 [1.7, 13.8], +0.2% | $13 [2, 25], +0.2% | $16 [3, 29], +0.2% | $20 [3, 37], +0.2% |
- Tier-1: bigger caps scale $ but ranges stay wide; 1-min edge stays +3.5-3.8% to cap 2,000 at 30 s, falls with longer windows.
- Smaller tournaments: tiny fills, but to-result is positive with ranges above zero (both halves), +6-12% of $ filled.
  1-min edge is small there, so the gain is the price catching up slowly over the rest of the map.
- $/day (estimate, queue ignored): tier-1 30 s cap 1,000: 5.6 x ~$24 = ~$135/day; smaller 60 s cap 1,000:
  13 x ~$12 = ~$155/day. **Together ~$250-300/day**, with a 90% range of roughly -$100 to +$700/day. A 2,000 cap on tier-1 would add
  ~$130/day on paper.
- Checks done: rules unchanged, beta from the top-250 training half (out of sample for smaller tournaments),
  lag +20 has no overlap with the round-time fit window.
