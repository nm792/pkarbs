# Independent audit: frozen mentions rule on Polymarket (909 post-burn events)

**Verdict: 3c = FAIL. 10c = PASS on the statistics, economically tiny. 5c = FAIL after correction. Confidence 7/10.**

I re-pulled every trade myself from the Polymarket data API (`/v2/trades?condition=...`, 17,438 markets in the 909 post-burn events; first 24 h of each market kept in `pm_trades_first24h.json.gz`) and rebuilt the rule from the events file. Code: `pmaudit.py`, `p1-p5.py`, full output `pm_audit_output.txt`.

## 1. Reproduction
Build's naive version: 3c +$1,732 on $3,898 (338 bets), same-event placebo ~$1,017 (build: $1,062); 10c +$2,409 on $3,001. Log score +0.125. Matches.
One difference: the build's `lockstat` same-event placebo scales each random print by `min(print size, bet size)`, which shrinks the placebo on small prints and flatters the real result. I use a placebo at the bet's own size (random BUY print of the same event). With it the 3c paired t is 1.49, not 2.27.

## 2. Causal base rates
The build adds an event to the word history in start order, before that event has resolved. I rebuilt it so an event enters the history only after every market in it had closed (`closedTime`) before the new event's start. Causal results below (naive in brackets):

| Rule | Bets | P&L | Same-event placebo (z) | Price-matched placebo (z) | Paired t | Cluster t month / week (real-minus-placebo) |
|---|---|---|---|---|---|---|
| 3c | 337 | +$1,637 on $3,807 [+$1,732] | +$1,017 (**1.5**) | +$1,045 (**1.2**) | 1.3 | 2.3 / 1.3 |
| 5c | 325 | +$2,087 on $3,660 [+$2,178] | +$992 (2.7) | +$1,051 (2.3) | 2.4 | 2.8 / 2.5 |
| 10c | 285 | +$2,342 on $2,970 [+$2,409] | +$857 (**4.3**) | +$917 (**3.7**) | **3.8** | 3.7 / 4.0 |

The leak is small (about 4-5% of P&L). Price-matched placebo: same family, same side, +/-3c, other events.

## 3. Held-out and other cuts (causal)
| | 3c | 5c | 10c |
|---|---|---|---|
| Later half (calendar, from 2 Jul 2026): P&L | +$1,283 | +$1,367 | +$1,376 |
| Later half: same-event z / price-matched z | 1.9 / 0.7 | 2.5 / 1.0 | **3.8 / 2.1** |
| Earlier half: P&L / same-event z | +$354 / 0.7 | +$720 / 1.7 | +$966 / **2.7** |
| Build-style per-family later half: paired t | 1.4 | 1.9 | 2.9 |

Only 10c is positive and significant in both halves. In the 3c later half the price-matched placebo (+$1,101) explains almost all of the real +$1,283.

**300-event sample (seed 7):** 3c +$620, same-event z 1.5; its later half z about 0 (paired t -0.08); 10c z 2.0 (later half 1.4). The 300-sample was a first look at the same 909 events, so it is not independent evidence.

**By family at 10c:** Trump events +$1,064 (125 bets, z 3.5/3.7); other +$537 (z 1.4/0.5); earnings calls +$325 (z 2.5/1.4); Trump weekly +$221 (z 1.1/0.9); sports announcers +$195 (z 0.8/0.9). The result is mostly Trump events.

**Concentration (10c):** top 3 bets $510 of $2,342; excluding the top 10 bets still +$1,258.

## 4. Variant count
Primary variants counted: Kalshi 9 series x 3 thresholds, the earlier Kalshi Trump run x 3 thresholds, Polymarket 300-sample x 3 thresholds, Polymarket 909 x 3 thresholds = 12. As a stress test 36 (adding the held-out cuts, families and window/anchor checks).
- 10c all events: paired t 3.81 (p 1.4e-4): x12 gives 0.002, x36 gives 0.005. Survives.
- 10c later half: t 3.58 (p 3.4e-4): x12 gives 0.004, x36 gives 0.012. Survives.
- 10c earlier half alone: t 2.44: x12 gives 0.18. Not significant alone.
- 5c: t 2.40 gives about 0.2 after x12. Fails. 3c fails outright.
Note the two venues passed at DIFFERENT thresholds (Kalshi 3c, Polymarket 10c); 10c is positive on Kalshi too (paired t 2.3, same-event z 2.7) but not significant there. Many Trump events appear on both venues, so the venues are not independent confirmation.

## 5. Fees
Markets created from March 2026 carry `feeType mentions_fees` (feeSchedule: rate 0.04, exponent 1, taker only). Applying fee = size x 0.04 x p(1-p) to those markets: $40 at 10c (+$2,342 gross), $47 at 3c. Even charging 4% on every market it is $68 / $80. Fees do not matter at these bet sizes (average bet $10). docs.polymarket.com is not reachable from this session, so the formula comes from the market's own `feeSchedule` field and is unconfirmed against the published fee page; the conclusion holds if the fee is several times larger.

## 6. Timing: "first hour" and executability
The window runs from the earliest `startDate` of the event's markets (market creation on Polymarket), not from the event itself. First trade comes a median 37 min after startDate (25% after 100 min), so the first hour is mostly waiting. Bets happen at a median 30 min lag (10th-90th percentile 14-53 min).
- Delay robust: a 15 min delay still gives 10c +$2,173 (t 3.8); 5 min and below no change.
- Anchoring on the first trade instead of startDate gives more bets (434) and still passes at 10c (+$3,550, z 5.8/2.9).
- Longer windows (6 h, 24 h) also pass at 10c; a 15 min window has only 37 bets. Executable only by a bot watching for new mention markets (creation is public) and taking the first resting ask that clears the threshold.

## 7. Size and the burn-in
- Average bet $10.4 (median 21 shares): bets are limited by the print size. Cap at 10 / 25 / 100 shares: +$590 / +$1,232 / +$1,961 at 10c, z stays above 3.9. P&L over 477 days is about $4.9/day; the later half about $11/day. Nothing like $500/day.
- Burn-in 15% / 50% and shrinkage alpha 1 / 5 and price range [0.02,0.98] / [0.10,0.90]: 10c stays at paired t 3.3-3.8. The 30% per-family burn-in is not driving it. But "family" is a title-keyword bucket (`other` mixes unrelated speakers with one shared word history) and the family assignment was fixed before outcomes, so no outcome look-ahead.
- 67 of 1,363 events were dropped (28 with fewer than 3 markets, 39 unresolved or 50/50 voided): a small, mild survivor filter.

## 8. Log score
+0.121 nats per market-event, market-level t 7.0 (not independent). Event-level (587 events): +0.115, t 4.0; week-cluster t 3.2. But it decays: earlier half +0.185 (t 3.7), later half +0.046 (t 1.6). Only Trump events are individually significant (+0.194, t 3.8).

## 9. What would raise confidence above 9
1. A forward test at 10c only on new events, judged once (the later-half log score has decayed).
2. Check whether fills at these prints are reachable in real time (needs recorded books at market creation).
3. Confirm the fee formula on the Polymarket fee page.

## Confidence
7/10. Data and checks reproduce from raw trades; unresolved: fee formula, real-time fill depth, decay of the model's edge over time, and that the passing threshold differs between venues.
