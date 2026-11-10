# Independent audit: Kalshi Mentions word-base-rate rule (9 series, 3c)

**Verdict: PASS on the statistics, with limits. Confidence 7/10.**
Not an edge worth sizing yet: the profit is tiny next to $500/day, and it needs a forward test. Nothing here is a live-trading approval.

Everything below was recomputed from raw Kalshi data (markets and trades pulled afresh from api.elections.kalshi.com, not from the build thread's files). Code and full output are in this folder (`audit.py`, `r1-r3.py`, `audit_output.txt`).

## 1. Reproduction
Same rule (online word base rate, 30% burn-in, first hour from open, first BUY print with edge >= 3c, full print size, hold to settlement), pooled over 9 series:

| | Build thread | Audit (own pull) |
|---|---|---|
| Bets | 595 | 596 |
| P&L | +$2,624 | +$2,626 on $25,344 |
| Fees | | $252, net $2,374 (build: $2,372) |
| Wins | 455 | 456 |

Reproduces. Differences are one extra print from a fresh pull.

## 2. Look-ahead (the build ordered events by open time)
The build adds an event's result to the word history as soon as the next event opens, even if that event had not settled yet (NBA/Trump markets open days before the game; one NBA event settled in October for a March game). The audit rebuilt it causally: an event only enters the history once ALL its markets had closed and settled (the earlier of `close_time` and `settlement_ts`, which is conservative) before the new event opened.
Result: +$2,700 on $25,140 (net $2,451), so the leak is not what produces the result. Word lists are the market's own `yes_sub_title` at open, so no after-the-fact word lists. 44 `scalar` and a few hundred blank (still active or closed) markets across series are excluded; none are voids that matter.

## 3. Locked checks, causal version, 3c
| Check | All events | Later half (calendar, from 23 Apr 2026) |
|---|---|---|
| Real P&L | +$2,700 (stake $25,140) | +$1,053 (stake $3,104) |
| Same-event random BUY-print placebo | +$800 +/- 573, **z 3.3** | +$357 +/- 238, **z 2.9** |
| Price-matched placebo (same series, same side, +/-3c, other events) | +$559 +/- 550, **z 3.9** | +$97 +/- 269, **z 3.6** |
| Paired t vs same-event placebo | 3.63 | 3.06 |
| Cluster t (month) | 2.79 (19) | 2.96 (8) |
| Cluster t (week), real vs 0 | 4.37 (70 weeks) | |
| Cluster t (week), real minus placebo | 2.96 (63 weeks) | |
| Top 3 bets | $351 of $2,700 | $241 of $1,053 |
| Excluding top 10 bets | +$1,856 | +$392 |
| Net of fees | +$2,451 | +$985 |

Build-style per-series second half: +$1,007, same-event placebo z 1.8, price-matched z 2.4, cluster t 2.3 (13 clusters).

**Price-matched placebo.** The build pooled it across series and got a NEGATIVE number (-$1,652). That is too easy a hurdle: NBA words are priced and resolve differently from Trump words. Matched within series it is positive (+$559 all, +$97 later half), and the real rule still beats it at z 3.6-3.9. The harder hurdle is the same-event placebo, as the build thread said.

**Concentration.** Not driven by a few bets. But by series: NBA is $18k of $25k stake (210 of 223 wins, mostly YES at ~91c) and its excess over placebo is only about +$500, z 1.5. Without NBA: +$1,435 vs same-event placebo +$42 (z 3.0), price-matched z 3.5, later half +$967 vs +$302, t 2.96. So the signal is not only NBA near-90c YES.

## 4. Variant count
Variants: 3 thresholds, plus the earlier Trump run (3 thresholds, test half), plus the held-out cuts. Taking 12 as a conservative count: all-events paired t 3.63 (p 0.0003) gives Bonferroni p ~0.004; later-half paired t 3.06 (p 0.002) gives ~0.03. Survives at 3c. **The 5c rule does NOT pass on all events** (paired t 1.07, same-event z 1.45); 10c is weaker (t 2.27, cluster t 1.79). Both pass in the later half only. Only 3c should be called tested.

## 5. Log score vs first print
+0.044 nats per market (causal), market-level t 5.1. That t counts 5,074 markets as independent, which they are not. Event-level (710 events): mean +0.030, **t 2.5**; clustered by week **t 1.8**; later half +0.049, t 2.9. Per series it is positive in 8 of 9, but NFL is negative and none is individually significant except Trump-Say (t 2.7). The base-rate model is a modest, not strong, improvement on the opening price.

## 6. Fees
All 9 series are `fee_type quadratic, fee_multiplier 1` (checked on `/series/<ticker>`), so the build's `ceil(0.07*C*P*(1-P))` is right for taker fills. Fees are about $252 on $25k stake (~1%); near 91c it is about 0.6c per contract. Fees do not erase the edge. (Maker fees not relevant: all fills are taker.)

## 7. Fill realism (the real weak point)
- 33% of bets are filled within 60 s of open; median 4 min. The rule buys the first print that clears the edge, at that print's full size.
- Delay test, all events: 5 s unchanged (+$2,710); 30 s +$1,864 (paired t 2.2); 60 s +$1,183 (t 1.4); 5 min +$500 (t 0.8). In the early half the edge is mostly stale opening quotes: speed matters.
- In the LATER half it is stable: +$1,063 at 5 s, +$985 at 30 s, +$1,136 at 60 s, +$787 at 5 min (t 2.4). So the recent edge is not a first-seconds artefact, but only the recent half shows that.
- Size is not the problem: capping each bet at 10 / 25 / 100 contracts keeps z 4.4-5.1 (P&L +$415 / +$892 / +$2,701). Realistic capacity is tens of dollars per bet.
- Historical order books are not available, so whether a taker could really have taken each print's full size at that price is unverified. Prints are real trades, which is the best available evidence.

## 8. Size of the prize
Later half: about +$1,000 net over ~6.5 months at the build's print sizes, +$415 to +$892 over the whole period at 10 to 25 contract caps. That is a few dollars a day against the $500/day target. Statistically real-looking, economically small.

## 9. What would raise confidence above 9
1. A forward test on new events (the later half is only 8 clusters; need 100+ new events), judged once.
2. Live order-book snapshots at market open to confirm full-size fills.
3. A pre-registered single threshold (3c) so the variant count stops growing.

## Confidence
7/10. Facts are reproduced from raw data and checks are in one place; the main gaps are the unverifiable fills, the small number of later-half clusters, and the weak (t 1.8-2.5) log score.
