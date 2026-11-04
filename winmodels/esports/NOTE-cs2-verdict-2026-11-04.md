# CS2 event-only rule: first verdict from historical data (4 Nov 2026, 06:00Z)

Confidence 6/10 (sample is 20 matches, not 100).

## Data
- Round scores: Polymarket sports WS as our server logger received it, 2 Nov 06:49Z - 4 Nov 04:00Z
  (rn1/scores/cs2/server-2026-11/cs2_changes.jsonl.gz). 27 matches carried round scores; 20 of them are CS2
  matches listed on Polymarket (the other 7 are Dota 2 EPL matches, which also carry live scores on the WS).
- Markets: 20 match-winner + 31 map-winner markets, 1,606 round changes. All trades via data-api /v2/trades
  (raw: /mnt/project-files/winmodels/raw/esports_cs2_2026-11-02_04.tar.gz; gamma events + 1,110 closed markets).
- Holdout = the later 10 matches by start time (3 Nov 11:30Z onward, mostly tier-2 plus Liquid-TYLOO);
  the price-response factor (beta) is fitted on the earlier 10 only.
- Scripts: cs2_maps.py (rule, holdout, delay), cs2_maps_fast.py (what-if earlier feed). Outputs out_cs2_maps*.json.

## 1. Feed delay (measured, 503 map-market rounds with model move >= 2c)
Average signed map-winner price move around the moment we receive the round from the WS (cents, cumulative from -60 s):
-30 s 1.8c | -20 s 3.5c | -10 s 5.2c | 0 s 5.8c | +10 s 6.5c | +60 s 7.4c.
- About 78% of the move is already in the price when the round reaches us; half the move happens ~15-20 s before.
  Same in the earlier and later halves (3-4 Nov half: 50% point ~16 s before receipt).
- So the Polymarket WS is ~15-20 s behind the market for CS2 rounds (round changes land on its 20 s heartbeat grid).
  This supersedes the 2 Nov "+0.4 s median" figure, which was measured on 75 changes against match-winner prices.

## 2. Event-only rule (bid mid x 0.975, maker only, side the model says should rise >= 1c but hasn't, 30 s window, corrected fills, held to result)
At the real feed timing (lag 0 after WS receipt), 500-share cap:
| set | markets filled | $ filled | 1-min edge | to result |
|---|---|---|---|---|
| holdout maps | 5 | $641 | +7.4% | +$192 |
| holdout match | 3 | $550 | +1.7% | +$72 |
| all 20 maps | 15 | $2,315 | -0.4% | +$235 |
| all 20 match | 8 | $2,684 | -5.3% | -$569 |
- Holdout: +$264 over 10 matches = ~+$26 per match. All 20 matches: -$334 = ~-$17 per match. Bootstrap ranges all span zero.
- What-if a feed 10-30 s earlier than the WS (cs2_maps_fast.py): no better. All 20 maps lose to result at every
  early lag (-36% to -43% of $ filled); match winner +5-9% at 1 min but flat to negative to result.
- The rule fills little: about $60-250 per market. The price has usually moved before the rule can act.

## Verdict
- No edge shown for the CS2 event-only rule, at the WS timing or with a faster feed. Best reading: ~$0 per match,
  range about -$20 to +$25 per match. At ~45 Polymarket CS2 matches/day with ~45% round coverage that is -$400 to +$500/day
  of noise, not a result.
- Why: CS2 rounds are visible to everyone watching the stream, and the market prices them ~15-20 s before the WS.
  Bids on the "should rise" side after the move mostly fill when informed sellers hit them.
- Firm verdict date: the logger adds ~10 Polymarket CS2 matches with round data per day, so 100 matches arrive by
  ~12 Nov; re-run cs2_maps.py then and well before the PGL Major (25 Nov).
- Faster route: a historical round source (bo3.gg API answers JSON, with map begin times; round timestamps not yet
  confirmed) would give 100+ matches today, but api.bo3.gg is not on the network allowlist.

## 3. rn1's CS2 pattern on the same 20 matches (cs2_resting.py, out_cs2_resting.json), 06:15Z
Resting bids at mid x 0.975 on both sides through play, pulled 30 s after each round, maker only, corrected fills,
held to result, plus estimated rebate. "Pull at WS" = we pull when the WS round reaches us; "pull 20 s earlier" =
what-if feed as fast as the market.
| cap | filter | pull | all 20: $/match | holdout 10: $/match | maps 1-min | match 1-min |
|---|---|---|---|---|---|---|
| 100 | none (rn1 style) | at WS | -$11 | +$15 | -0.9% | -1.9% |
| 100 | none (rn1 style) | 20 s earlier | +$48 | +$23 | +0.2% | -2.0% |
| 500 | none (rn1 style) | at WS | -$5 | -$122 | -0.6% | -1.5% |
| 500 | none (rn1 style) | 20 s earlier | +$155 | -$126 | +0.7% | -1.6% |
| 100 | model filter E=2c | at WS | +$126 | -$151 | -1.4% | +0.4% |
| 500 | model filter E=2c | at WS | +$584 | -$316 | -1.6% | +0.9% |
- Volume: ~$2.4k filled per match at the 100 cap; rebates ~0.35% of $ filled (~$8/match), vs rn1's 0.46%.
- Every to-result range spans zero by thousands of dollars: holding to result on 20 matches is outcome luck.
  The model-filter rows flip sign between all-20 and holdout, so they say nothing yet.
- The steadier number is the 1-min markout: resting bids lose ~1-2% in the first minute when pulled at WS time
  (rn1's own maker fills: -0.97% first minute, entry 2.54% below market, +0.96% net to result). Pulling 20 s earlier
  brings map markets to ~0, which is worth ~$60/match at the 100 cap on these 20 matches.
- Reading: rn1's pattern is about break-even on our feed timing in this sample; it is consistent with rn1's thin
  ~1% maker margin, but 20 matches cannot separate +1% from 0. Needs the ~100-match re-run (~12 Nov).
