# Perp vs Polymarket "SPY Up or Down on <date>" (daily close): LOCKED RULE (Reviewer prototype, 19 Nov 2026 ~02:30Z)

Nick 02:20Z: "the simplest perp test is the SPY v this" (spy-up-or-down-on-november-19-2026). Written and committed before any model probability, edge or P&L is computed. Seen so far: the event description, the 19 Nov event's current price (0.71/0.29) and fee field, and the fetch log (trade counts, gamma volume). Analysis only, no orders.

## Market
Resolves Up if SPY's close on D > SPY's close on the prior trading day; Down if lower; 50-50 if equal. Each event trades from about 13:00Z the prior day. Each token priced only from its own trades (SETTLED A1). Fee per share 0.04 x p x (1-p), taker only (feeSchedule; formula per mfw-clone results/T004).

## Data (public, no keys)
Polymarket gamma events `spy-up-or-down-on-<month>-<day>-<year>` for every weekday 20 Apr - 18 Nov 2026, all trades per condition from data-api v2 (`fetch_pm.py`, `data/`). Perp: Hyperliquid xyz:SP500 1 h candles; ^GSPC Yahoo daily bars, copied from pkarbs main d9f9f905 `weekend-perps/backfill-2026-11-16/data/` (Hyperliquid and Yahoo are blocked from this container).

## Universe
Events with date D such that Yahoo has bars for D and the prior trading day, D in 22 Apr - 13 Nov 2026.

## Definitions (one each)
- Close time K = Yahoo bar timestamp of D + 6.5 h (20:00Z EDT / 21:00Z EST; an hour boundary). C0 = prior Yahoo ^GSPC close.
- Checkpoints: every hour boundary t = K - k h, k = 1 ... 23 (covers the overnight and the session). Skip a checkpoint with no candle ending at t.
- Perp price P_t = close of the Hyperliquid 1 h candle ending at t (last trade before t). x_t = ln(P_t / C0).
- Outcome y = ln(Close_D / C0) (^GSPC, Yahoo). Residual e_k = y - x_t.
- Model: p_up(t) = Phi((x_t + mu_k) / sigma_k), mu_k and sigma_k = mean and sd of e_k on TRAIN days, per k. (SPX index used for SPY: dividend days differ; the payout uses Polymarket's own resolution.)
- Own-token ask: last taker BUY print of that token in [t - 5 min, t] (strictly before or at the decision). None = that side skipped, counted.
- Edge = p_model - ask - fee(ask). Trade the side with the larger edge if edge >= 0.03 (fixed). At most one trade per (event, checkpoint). Hold to resolution; payout from `outcomePrices`.
- Size: notional = 10% of USD notional of taker BUYs of that token in [t - 60 min, t]. $/day = sum of realised $ / universe days.

## Split
TRAIN 22 Apr - 31 Jul (fits mu_k, sigma_k only). TEST 1 Aug - 13 Nov. Verdict on TEST.

## Reported
Reconciliation of pulled shares vs gamma volume per event, and USD notional per event by month. Calibration (Brier, sign hit) per k band. Trades, hit, mean ask, ex-ante edge, realised per share, $/day, tradeable $ per day; 95% CIs by bootstrap over days (10,000, seed 1). Breakdown overnight (k >= 7) vs session (k <= 6).

## Controls
1. Sign-flip placebo (swap p_up and p_down): expect realised per share < 0.
2. Planted 5c edge (ask set so edge = 0.05): every checkpoint with an ask trades, ex-ante edge = 0.05, realised about +0.05.
3. Null plant (ask = p_model): zero trades.

## Verdict (locked)
PASS needs on TEST: >= 20 trades; realised per-share CI lower bound > 0; $/day CI lower bound >= $200 before rebates; placebo < 0; plants behave. Plants fail = INVALID. < 20 trades = UNDERPOWERED. Else FAIL.

## Live read (19 Nov)
One read of the 19 Nov event's own books (both tokens) from the CLOB `/book` endpoint, timestamped. The perp side cannot be read live from this container (Hyperliquid blocked); it is reported as missing, not filled.
