# LOCKED RULE: does the Polymarket perp predict the cash open well enough to beat the price of the Polymarket "Opens Up or Down" contracts? (19 Nov 2026 ~02:50Z, written before any model number, edge or P&L of this test was computed)

Order: reviewer/REVIEW-2026-11-18-perp-open-contracts.md (Reviewer 18 Nov), Nick 18 Nov 08:31Z. Goal: strategies that make $200/day before rebates and can be stacked (SETTLED A9). Desk analysis on public data, no orders.

## What was looked at before locking (counts and formats only, no prices of the model)
- Gamma API: 268 events titled "... Opens Up or Down on <date>?" found by search: 197 "S&P 500 (SPX)" (22 Jan to 19 Nov 2026) and 71 "SPY". No Nasdaq, Dow or single-stock open markets were found by search ("Nasdaq", "NVDA", "Dow", "Tesla" queries): the universe is SPX and SPY only.
- Resolution (from the market description): Up if the official open of the day is HIGHER than the official close of the most recent prior trading day, Down if lower, 50-50 if equal. There is no strike: the perp-implied probability is P(open > prior close).
- Each event has one market with two tokens (Up, Down), opens for trading the afternoon before (about 13:01Z), taker fee schedule rate 0.04, exponent 1 (gamma feeSchedule).
- Own-token trades (side, price, size, timestamp) are available from data-api /v2/trades by condition id. Historical order books are NOT available from Polymarket, and this project holds no recorded book for these markets.

## Universe (fixed)
Every resolved SPX and SPY open event for trading days 3 Aug 2026 to 18 Nov 2026 (the Polymarket perp has history only from 1 Aug 2026). Rows where the market resolved 50-50, has no resolution, or lacks Yahoo bars are dropped and counted. The 19 Nov event is unresolved and excluded.

## Data and definitions (fixed)
- Cash open time T = 09:30 America/New_York on the event date (daylight saving by the tz database).
- Perp price S_k = last 1 s mark of Polymarket perp SP500-USD (mark-history, interval 1s) at or before T - k minutes, k in {60, 30, 10}; the point must be within 120 s of T - k, else the checkpoint is skipped and counted. Primary checkpoint k = 30 (declared now); k = 60 and 10 are reported as sensitivities, not alternatives.
- Prior close C and open O: Yahoo Finance daily bars (chart API) for ^GSPC (SPX events) and SPY (SPY events), unadjusted. SPY: the dividend of an ex-dividend date is added back to the open (O + dividend) so the comparison is clean; the dividend comes from the same Yahoo response. Outcome for P&L = the Polymarket resolution (outcomePrices); the Yahoo open-vs-close sign is only a data check (agreement rate reported).
- Perp return x_k = ln(S_k / C_SPX), where C_SPX is the ^GSPC prior close (the perp is on the index, for both SPX and SPY events). Realised open return y = ln(O / C) for the contract's own underlying.
- Model: y ~ Normal(x_k, s^2), so P(Up) = Phi(x_k / s) and P(Down) = 1 - P(Up). s = standard deviation of (y - x_k) over the TRAINING half only, separately for SPX and SPY. No other parameter is fitted (no bias, no slope). Train = the earlier half of the event dates (by date, both products), test = the later half. The test half is the verdict; train-half and full-sample numbers are shown but carry no verdict.
- Price of a side = ASK OF ITS OWN TOKEN (never 1 - the other token, SETTLED A1, B2). Two evidence levels, always reported separately:
  (a) BOOK level: the best own-token ask from a recorded book at the checkpoint. Rows without a recorded own-token book are EXCLUDED AND COUNTED. Expected n = 0 on history. If n < 30 events the verdict at this level is "unknown, N too small".
  (b) FILL-PROXY level (labelled PROXY, not a book): the size-weighted average price of BUY-side taker trades in that token in the window [T - k min, T - k min + 120 s]; rows with no such trade are excluded and counted. A taker buy pays the ask, so this is the price actually paid, but it is not the quote available at the checkpoint and it is selected on rows where someone chose to buy. Depth = shares bought in the same window (shares and USD at the proxy price).
- Fee: taker fee in USDC = shares x 0.04 x p x (1 - p) (Polymarket docs, https://docs.polymarket.com/trading/fees, category Finance 0.04, read 19 Nov 2026; matches gamma feeSchedule rate 0.04 exponent 1). Makers pay none. Taker rebates (programme) are NOT counted here; reported separately only if computable.
- Edge per share for a side = P(model) - ask - fee per share. Trade a side when edge > 0.03 (3 cents, fixed now; 0.01 and 0.05 are sensitivities). At most one side per event and checkpoint (the larger edge). Hold to resolution: P&L per share = 1{side wins} - ask - fee per share.

## Metrics (all reported, test half is the verdict)
Rows, exclusions with reasons; hit rate vs mean ask; mean net P&L per share with an event-cluster bootstrap CI (cluster = trading date, SPX and SPY on the same date are one cluster, 10,000 resamples, seed 1); depth; $/day at 10% of the fill-proxy depth (USD per trading day = sum over trades of 0.10 x shares bought in the window x net P&L per share, bootstrap CI over days); sign-flip placebo (replace x_k by -x_k with the same s, asks, thresholds and fee: must lose); matched check that the Yahoo and Polymarket outcomes agree; correlation of daily P&L with the other candidates is NOT computable here (no common daily series exists in this repo) and is stated as unknown; capital tied = sum of ask x shares bought per day.
A hard ceiling is also reported: total own-token USD volume traded per event in the checkpoint window and per event in the last 60 minutes before T, and $/day if 100% of the best side's volume at the model edge were captured. If that ceiling is below $200/day the verdict is "fails on size" whatever the edge.

## Verdict (locked)
PASS needs, on the test half at fill-proxy level: n >= 30 trades over >= 20 distinct dates AND mean net P&L per share > 0 with CI lower bound > 0 AND the sign-flip placebo mean < 0 AND $/day at a 10% slice with CI lower bound >= $200 (before rebates). Otherwise: "fails on edge" (CI includes or is below 0), "fails on size" (edge positive but $/day CI lower bound < $200), or "unknown, N too small". At BOOK level only "unknown, N too small" or a number with its n; the fill-proxy result alone never promotes to a deployable claim, only to "forward book recording is justified".

## Tests that must be able to fail (committed with the code, run before the real data)
1. Planted edge: asks set 5 cents below the model probability must return mean net edge about +5 cents minus fee.
2. Zero edge: asks equal to the model probability must return about minus the fee (negative), never positive beyond noise.
3. Sign-flip: a model with x replaced by -x on a planted-edge copy must lose.
4. Exclusion: rows without a book or fill must be excluded and counted, not filled.
5. Timing: checkpoint, window and open-time functions are tested on a known date across daylight-saving (a date in August and one in December).

## Forward recording (same day)
A read-only recorder (weekend-perps/open-contracts-2026-11-19/book_recorder.py, committed with a test) logs own-token books for every open event every 10 s from 13:01Z of the day before until the open + 5 min. The agent only deploys it by commit SHA. Book-level evidence accrues one event per product per trading day: 30 events is about 15 trading days (SPX plus SPY same day count as two events, one cluster).

No threshold, definition or checkpoint above may change after the first model number is seen. Any new idea needs a new rule file.
