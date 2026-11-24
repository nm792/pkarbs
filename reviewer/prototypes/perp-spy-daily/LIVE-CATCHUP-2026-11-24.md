# Live catch-up check, 24 Nov 2026 (Reviewer). Window 1: 13:22-15:18Z (US open 14:30Z)
Rule `CATCHUP-RULE.md` live section (2049e5a5). Code `live_catchup.py` (C0 for the 24 Nov event = Polymarket perp mark at 23 Nov 21:00Z close, 7237.8, mark-history ts 1795467599000; known before this window). Log `live_2026-11-24_w1_book_v2.jsonl.gz` (6,801 rows, 1 s, perp mark + perp bid/ask + both SPY books). Output `live_catchup_result_2026-11-24_w1.json`. 15-min check at 13:39Z passed (0.96 rows/s, 0 errors, book live: Up 0.12-0.24 then 0.15-0.43 over the window, median spread 3c). Read-only; nothing traded.

## Result (n is tiny; descriptive)
- 8 perp moves of >= 10 bp in 60 s. Quote lag (stale token's book mid covering half the model jump): 4, 5, 21, 35, 39, 82, 124, 131 s. **Median about 37 s**, against a 253 s median for trade prints over 79 events. The books reprice faster than prints show, but not instantly.
- Trades at the real ask (5 shares, taker fee both legs, exit at the real bid on catch-up or a 15-min stop): **3 trades**, all exited on catch-up:
  - 14:50:41Z, perp +17.4 bp, model jump +0.091: bought Up at 0.34, sold at 0.39 after 566 s, **+3.2c**/share
  - 15:01:19Z, perp -10.9 bp, jump -0.072: bought Down at 0.63, sold at 0.67 after 279 s, **+2.2c**
  - 15:12:23Z, perp +10.1 bp, jump +0.050: bought Up at 0.34, sold at 0.36 after 143 s, **+0.2c**
  - Mean +1.8c/share, $0.28 total at 5 shares. The other 5 moves: the ask was already above the catch-up target (book had moved within a second, or the jump was too small against a 3c spread).
- Planted 30 s catch-up: measured 30.2-30.7 s where the real book had not already caught up; plant trades captured on all 8 moves.
- Ask sizes at entry: 59.7, 50.0, 80.5 shares, so up to ~$20-27 per trade at the touch.
