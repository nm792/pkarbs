# SPY daily Up/Down: 5-minute underlying vs Polymarket prints (locked before scoring, 19 Nov 2026 ~04:10Z)

Purpose: first family from the pipeline screen (SPY daily close). Question: do Polymarket taker prints trade at prices the SPY
price already made stale, and is the money worth taking at real size? Reviewer's hourly perp test (reviewer/prototypes/perp-spy-daily,
RESULT.md) was FAIL on hourly checkpoints and INCONCLUSIVE on lag; its container could not reach Yahoo. This one uses Yahoo SPY 5-minute
bars (incl. pre/post market), reachable from this container, so it covers every print, not hourly checkpoints. Not a repeat: different data, print-level.

Data: Yahoo SPY 5 m bars 27 Aug-18 Nov 2026 (`range=60d&interval=5m&includePrePost=true`); Polymarket SPY Up/Down events and trades from
the Reviewer's `data/events.json` and `data/trades_<date>.json.gz` (pulled 19 Nov by fetch_pm.py, v2 trades). Each token priced from its own prints.

Definitions: C0 = last regular-session (09:30-16:00 NY) 5 m bar close on the prior trading day. Close K = 16:00 NY on D. Underlying at print time s =
close of the last 5 m bar that ended at or before s (bar start + 300 s <= s). x = ln(P/C0). Model p_up = Phi(x / sigma_tau), tau = hours to K bucketed
(<=0.5, 1, 2, 3, 6, 12, 24, 48); sigma_tau = sd of ln(Close_D/P) on TRAIN days in that bucket (mean 0). Token probability p = p_up (Up) or 1 - p_up (Down).
Decision per print: taker BUY print of a token at price q with fee 0.04*q*(1-q) per share; trade if p - q - fee >= 0.03. Hold to resolution; payoff from the event's final prices.
Size: 10% of the USD of qualifying prints (a taker could not take more than was printed). Per-day $ = sum / number of test days.

Split: TRAIN 27 Aug-7 Oct (fits sigma only); TEST 8 Oct-18 Nov. Verdict on TEST.
Controls: (1) sign-flip placebo (swap p and 1-p): expect negative; (2) planted: set q = p - 0.05 on every print: realised ~ +0.05 and ex-ante 0.05 after fee; (3) null: q = p: zero trades.
Reported: trades, USD, mean q, ex-ante edge, realised per share and $/day with 95% CI by bootstrap over days (10,000, seed 1); split by hours-to-close (<=3 vs >3) ; top-5-day concentration.
PASS: >= 20 trades, realised per-share CI lower bound > 0, placebo < 0, controls behave, AND $/day lower CI bound > 0. Else FAIL (or UNDERPOWERED if < 20 trades).
