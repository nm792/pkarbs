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

## Window 2: 15:18-17:15Z (`live_2026-11-24_w2_book_v2.jsonl.gz`, 6,847 rows; output `live_catchup_result_2026-11-24_w2.json`; 15-min check at 15:36Z passed: 0.95 rows/s, 0 errors, book live)
- 10 moves. Quote lag: 5, 7, 11, 13, 14, 20, 35, 52, 107, 512 s.
- 2 trades: 15:21:45Z bought Down at 0.76 (only 5 shares at the ask), sold 0.77 after 39 s, -0.4c; 15:42:25Z bought Down at 0.84, sold 0.85 after 46 s, -0.05c. 8 moves skipped: the ask had already moved past the catch-up target at the first poll (and from 15:50Z the market was at 0.88-0.93 or 0.07-0.15, where a 10 bp move shifts the probability by about 1-2c).
- Planted 30 s: measured 30.2-30.8 s where the book had not already moved; plant trades on all 10 moves.

## Both windows (24 Nov, 13:22-17:15Z)
- 18 moves; quote lag median about 28 s (4 s to 512 s; 7 of 18 under 15 s).
- 5 trades: +3.2c, +2.2c, +0.2c, -0.4c, -0.05c. Mean **+1.0c per share**, $0.25 total at 5 shares. 13 of 18 moves gave no entry because the ask had already moved.
- Scale against the bar: at the observed ~5 trades/day, ~50-80 shares at the touch and +1c, this is about $2-4/day before any doubt about the sign. Detecting a 1c edge needs a few hundred trades (weeks of logging at this rate).

## Fee correction (applies to both windows above)
This market's own feeSchedule is rate 0.05 (`finance_prices_fees`, taker only), not the 0.04 the rule locked from older SPY events (gamma, read 24 Nov ~17:20Z). At 0.05 on both legs, the five trades are +2.69, +1.73, -0.27, -0.80, -0.31c: **mean +0.61c per share**, 2 of 5 positive.

## Parallel run by another Reviewer session (merged here unchanged; the two runs used separate loggers over overlapping windows)
## Live catch-up rerun, 24 Nov 2026, 14:07-16:04Z (Reviewer; the owner thread did not run it, due 13:15Z)
Rule: CATCHUP-RULE.md live section (2049e5a5), unchanged. Code: live_catchup.py. The only edit adds C0 for 24 Nov = Polymarket perp mark at 23 Nov 20:59:59Z, 7237.8 (ts 1795467599000), the same rule as 23 Nov's C0.
Log: live_2026-11-24_session_book_v2.jsonl.gz, 6,793 rows at about 1/s with 1 error row, from this Reviewer container (book_logger_v2.py). Read-only; nothing traded. The market was live and undecided (Up 0.18/0.21 at start, 0.20-0.88 over the window).

### Result (real, 116.7 min)
- 11 perp moves of 10 bp or more.
- 6 skipped: the ask had already caught up.
- 5 trades at 5 shares each. Mean **+1.23c per share after fees** (fee 0.04 x p(1-p) as locked). Total +\$0.31.
  - 4 of 5 positive: +3.15, +2.18, +0.18 and +0.67c; one -0.05c.
  - All exited "caught_up" after 45-565 s.
- Quote lag (stale token's mid covering half the jump): 4.0, 4.1, 33.6, 33.8, 37.4, 82.1, 106.9, 132.1, 220.7 and 510.5 s; 1 never.
- Planted 30 s catch-up control: 11 of 11 trades, +2.07c per share. The code finds a planted edge.

### Reading
- First live day with a tradeable book: positive, but 5 trades is far too few for any verdict (MODELLING-PRINCIPLES s2/s13).
- Size is the limit: displayed ask size at entry was 5 to 80 shares. At \$200/trade the rule would walk deeper asks; not measured.
- FEE CORRECTION (read 16:07Z): this market's own feeSchedule is finance_prices_fees, rate 0.05, takerOnly, rebateRate 0.25, not the locked 0.04. Both legs are taker, so at 0.05: real **+0.84c per share** (+2.69, +1.73, -0.27, +0.34, -0.31c; 3 of 5 positive); planted +1.74c. The rule file keeps 0.04; any later scoring uses the market's own rate (SETTLED A4).
- The logger is running again from 16:05Z for the rest of the session (to about 18:00Z), and a second read follows.
