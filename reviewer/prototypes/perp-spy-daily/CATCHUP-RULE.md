# Catch-up trade on the perp lag: LOCKED RULE (Reviewer, 23 Nov 2026 ~14:10Z, before any number)
Nick 14:03Z: the earlier tests held to resolution and buried the lag. This tests the trade that monetises it. Read-only analysis; no orders.

## Historical version (79 SPY events, 3 Aug - 20 Nov; inputs as LAG-RULE-v2.md)
- Move at second t: |ln(P_t/P_{t-60s})| >= 10 bp on the Polymarket perp SP500-USD 1 s mark; skip 10 min after a move. Only moves with a PM pre-level (median implied p_up of prints in [t-10 min, t-60 s]). dp = model fair jump over the minute (as v2).
- Stale token: Up for an up move, Down for a down move. Its pre-price q0 = L (Up) or 1-L (Down).
- Entry: the first taker BUY print of the stale token in [t+0.25 s, t+N] (0.25 s = the market's taker hold), N = 60 s primary (30, 120 reported), and only if its price <= q0 + |dp|/2 (still stale). Price = that print (a real ask fill). Size = min(5, print size) shares.
- Exit: the first taker SELL print of that token (a real bid fill) after entry with price >= q0 + |dp|/2 (caught up), or the time stop S = 900 s primary (300 reported): then the first taker SELL print after the stop. No SELL print before the close: exit at resolution, counted and flagged.
- P&L per share = exit - entry - 0.04*entry*(1-entry) - 0.04*exit*(1-exit) (taker fee both legs; at resolution no exit fee).
- Report: trades, mean P&L per share and $ per trade, hit rate, 95% CI by bootstrap over events (10,000, seed 1); by move size (10-20 bp, >20 bp), time of day (US session 09:30-16:00 ET vs outside), entry delay (<=10 s, 10-30 s, 30-60 s); 15 concrete trades; $/day.
- Controls: (1) Null: same entry/exit at random seconds with no move (same count, random direction, seed 1); expect mean <= 0 (spread + fees). (2) Planted 3c edge: add +0.03 to every real trade's P&L; report whether the CI lower bound is then > 0, i.e. whether this sample can detect a 3c edge. (3) A "no edge" verdict is allowed only if (2) detects.

## Live version (today's 1-2 s logger, `live_2026-11-23_book*.jsonl`)
Same move rule on the logged perp mark. Entry at the stale token's logged best ask on the first poll at or after t+0.25 s, size min(5, ask size); exit at its logged best bid when the bid >= q0 + |dp|/2 or after 900 s. q0 = stale token's mid on the poll before the move. Planted check: a synthetic book that jumps 30 s after each move must be captured.
