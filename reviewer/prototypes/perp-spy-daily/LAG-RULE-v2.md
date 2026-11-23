# Lag test v2, full run (Reviewer, 23 Nov 2026 ~14:00Z). Fixed before any v2 number is computed.
Why: v1 (`LAG-RESULT.md`) had one day of minute data. api.perpetuals.polymarket.com is now reachable (environment change approved 19 Nov), giving 1-second Polymarket SP500-USD perp marks back to 1 Aug 2026. Exploratory measurement with controls; no trade verdict. No orders.

## Universe
Every Polymarket "SPY Up or Down on <date>" event, 3 Aug - 20 Nov 2026 (Fri 20 Nov is the last resolved one). Event window: from its first print to its close K (16:00 ET; 20:00Z EDT / 21:00Z EST).

## Data
- Perp: Polymarket perps `mark-history`, instrument 1 (SP500-USD), interval 1s, over each event window (`fetch_perp_1s.py`).
- Polymarket prints: data-api v2 trades per condition (already in `data/` for events to 18 Nov; 19-20 Nov pulled the same way).
- C0 (prior SPY close level for the fair value): perp mark at the prior close time K_prev (last 1 s mark at or before K_prev). Checked against Yahoo ^GSPC prior closes on the overlap (to 13 Nov) and the median |difference| reported. Yahoo is still blocked.

## Definitions (same as v1 LAG-RULE.md except the perp source and resolution)
- fair p_up(t) = Phi((ln(P_t/C0) + mu(tau))/sigma(tau)), P_t = last 1 s mark strictly before t; mu, sigma interpolated in hours-to-close from TRAIN `result.json` (unchanged; beyond 23 h sigma_23 x sqrt(tau/23)).
- Move: |ln(P_t / P_{t-60s})| >= 10 bp (1-minute window, measured each second); after a move, skip 10 min. dp = fair(t) - fair(t-60s).
- PM pre-level: median implied p_up (Up price, or 1 - Down price) of prints in [t-10 min, t-60s]. None = not measurable, counted.
- Lag: seconds from t to the first print whose implied p_up covers half of dp from the pre-level, direction-aware. Censored at 30 min.
- Print gap: seconds from t to the first print of any kind (so lag can be split into "waiting for a trade" vs "trades still at the old price").
- Stale buy: taker BUY with price < fair(token at the print second) - fee(price) - 0.01. Report count, USD, and realised P&L at resolution; per event and in total; 95% CI by bootstrap over events (10,000, seed 1).

## Controls
1. Planted lag: insert one synthetic print exactly 30 s after each measurable move, at pre-level + dp. Lag code must report 30 s for every planted move where no real print caught up first.
2. Null times: same lag code at random seconds with no move (same count, seed 1, random direction, dp set to the median |dp| of real moves). The share "caught up" within 5 min must be clearly lower than for real moves, or the lag number is just print noise.
3. Stale-buy placebo: same stale test with fair computed from the perp 30 min earlier (stale model). Its realised P&L should be worse than the real model's.

## Live
One live read today (23 Nov) during the US session: perp mark (Polymarket perps and Hyperliquid xyz:SP500) and both SPY tokens' books at the same second, with fair p, ask and edge. Read at the decision moment; nothing traded.
