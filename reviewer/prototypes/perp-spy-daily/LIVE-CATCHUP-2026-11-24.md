# Live catch-up rerun, 24 Nov 2026, 14:07-16:04Z (Reviewer; the owner thread did not run it, due 13:15Z)
Rule: CATCHUP-RULE.md live section (2049e5a5), unchanged. Code: live_catchup.py. The only edit adds C0 for 24 Nov = Polymarket perp mark at 23 Nov 20:59:59Z, 7237.8 (ts 1795467599000), the same rule as 23 Nov's C0.
Log: live_2026-11-24_session_book_v2.jsonl.gz, 6,793 rows at about 1/s with 1 error row, from this Reviewer container (book_logger_v2.py). Read-only; nothing traded. The market was live and undecided (Up 0.18/0.21 at start, 0.20-0.88 over the window).

## Result (real, 116.7 min)
- 11 perp moves of 10 bp or more.
- 6 skipped: the ask had already caught up.
- 5 trades at 5 shares each. Mean **+1.23c per share after fees** (fee 0.04 x p(1-p) as locked). Total +\$0.31.
  - 4 of 5 positive: +3.15, +2.18, +0.18 and +0.67c; one -0.05c.
  - All exited "caught_up" after 45-565 s.
- Quote lag (stale token's mid covering half the jump): 4.0, 4.1, 33.6, 33.8, 37.4, 82.1, 106.9, 132.1, 220.7 and 510.5 s; 1 never.
- Planted 30 s catch-up control: 11 of 11 trades, +2.07c per share. The code finds a planted edge.

## Reading
- First live day with a tradeable book: positive, but 5 trades is far too few for any verdict (MODELLING-PRINCIPLES s2/s13).
- Size is the limit: displayed ask size at entry was 5 to 80 shares. At \$200/trade the rule would walk deeper asks; not measured.
- FEE CORRECTION (read 16:07Z): this market's own feeSchedule is finance_prices_fees, rate 0.05, takerOnly, rebateRate 0.25, not the locked 0.04. Both legs are taker, so at 0.05: real **+0.84c per share** (+2.69, +1.73, -0.27, +0.34, -0.31c; 3 of 5 positive); planted +1.74c. The rule file keeps 0.04; any later scoring uses the market's own rate (SETTLED A4).
- The logger is running again from 16:05Z for the rest of the session (to about 18:00Z), and a second read follows.
