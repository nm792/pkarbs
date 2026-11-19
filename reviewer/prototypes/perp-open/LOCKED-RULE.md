# Perp-priced Polymarket SPX open contract: LOCKED RULE (Reviewer prototype, 19 Nov 2026 ~02:30Z)

Written and committed before any model probability, edge or P&L was computed. Only things looked at so far: event counts, trade counts and volume per event (fetch log), the fee schedule field, and the date ranges of the saved perp/Yahoo files. Prototype by the Reviewer on Nick's instruction (19 Nov 01:45Z) because PK arbs dropped IDEAS.md row 0. Analysis only. No orders.

## Question
Does the Hyperliquid SP500 perp, 30 minutes before the US cash open, price Polymarket "S&P 500 (SPX) Opens Up or Down on <date>" better than that token's own ask, by more than the fee, with size worth $200/day?

## Data (public, no keys)
- Polymarket: gamma events by slug `spx-opens-up-or-down-on-<month>-<day>-<year>`, every weekday 20 Apr - 18 Nov 2026 (147 events found); all trades per condition from data-api v2 (`fetch_pm.py`, raw in `data/`). Fee: market `feeSchedule` {rate 0.04, exponent 1, takerOnly}; fee per share = 0.04 x p x (1-p) (formula as recorded from Polymarket's fee page in mfw-clone `results/T004/t004_schedule_sources.md`; docs.polymarket.com is not reachable from this container).
- Perp: Hyperliquid `xyz:SP500` 1 h candles, and ^GSPC Yahoo daily bars, as saved in pkarbs `weekend-perps/backfill-2026-11-16/data/` (main branch d9f9f905). Hyperliquid and Yahoo are blocked from this container, so no newer perp data.

## Universe
Every event whose date D has a Yahoo ^GSPC bar and a prior bar, and a Hyperliquid 1 h candle ending at T-30: 22 Apr - 13 Nov 2026. Mondays and weekdays alike. Missing rows counted, not filled.

## Definitions (one each, no variants)
- T = timestamp of the Yahoo bar for D (the cash open; DST handled by the data). C = previous Yahoo bar close. O = Yahoo open of D.
- Perp price P = close of the Hyperliquid 1 h candle that ends at T-30 min (an hour boundary in both EST and EDT). Trade price, not mid: proxy, labelled.
- S = (P - C) / C. Residual R = (O - C)/C - S.
- Model: p_up = Phi((S + mu) / sigma), p_down = 1 - p_up, where mu and sigma are the mean and sd of R on TRAIN days only.
- Own-token ask (SETTLED A1: each token priced only from its own trades/asks, never mirrored). Data-api trade `side` = the taker's side. PRIMARY: the price of the last taker BUY of that token in [T-35, T-30] min (a price that was available at or just before the decision). SECONDARY (reported, not used for the verdict): first taker BUY of that token in [T-30, T-25] min (delayed entry). A side with no such trade has no ask: that side is skipped and counted.
- Edge (ex ante) = p_model(token) - ask - 0.04 x ask x (1 - ask). Trade the token with the larger edge if edge >= 0.03 (fixed now, not tuned). At most one trade per day. Hold to resolution.
- Realised P&L per share = payout - ask - fee, payout from Polymarket resolution (`outcomePrices`: 1, 0, or 0.5 for 50-50).
- Size: notional per trade = 10% of the USDC notional of taker BUYs of that token in [T-60, T] min. $/day = total realised $ / number of universe days in the period (no-trade days count as 0).

## Split
TRAIN 22 Apr - 31 Jul 2026 (fits mu and sigma only). TEST 1 Aug - 13 Nov 2026. Verdict on TEST.

## Reported
Rows, exclusions by reason; model calibration on TEST (Brier vs 0.25, hit rate of sign(S+mu)); trades, hit rate, mean ask, mean ex-ante edge, mean realised P&L per share, depth proxy, $/day; 95% CI by bootstrap over days (10,000, seed 1); secondary entry; the same with p from the token's market price (no model) as a sanity row.

## Controls (the test must be able to fail and pass)
1. Placebo: swap p_up and p_down (sign flip of the signal). Expect realised P&L per share < 0.
2. Planted edge: replace every ask with p_model - 0.05 - fee(ask) solved numerically. The code must trade every row with ask available and report ex-ante edge 0.05; realised mean must be about +0.05 if the model is calibrated.
3. Null plant: asks set to p_model. The code must make zero trades.

## Verdict (locked)
PASS needs all on TEST: >= 20 trades; realised P&L per share 95% CI lower bound > 0; $/day 95% CI lower bound >= $200 (before rebates; rebates 25% of fees reported separately); placebo mean < 0; both plants behave as stated. If the plants fail, the result is INVALID. If trades < 20, "UNDERPOWERED". Otherwise FAIL. Never "promising".

## Known limits (stated before results)
Trade prints are not a book: a taker BUY print is at or above the best ask at that instant, so the primary ask is conservative on price but says nothing about depth beyond what printed. Perp price is an hourly candle close, so only T-30 can be tested; T-60 and T-10 need minute data or the live logger. Yahoo ^GSPC open is a proxy for the official open (resolution uses Polymarket's own outcome).
