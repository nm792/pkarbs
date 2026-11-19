# Result: does the Monday open overshoot or undershoot the weekend perp? (rule: LOCKED-RULE-overshoot-2026-11-16.md, merged before any number)

Sample: 1,005 cells with |S| >= 50 bp, 61 symbols, 29 weekends (22 Apr-16 Nov 2026 backfill). D = sign(S) x (O - S): positive = open went further than the perp, negative = open fell back toward Friday close. Median hurdle 14.8 bp. CIs by weekend-cluster bootstrap. "wk neg" = weekends (with >= 3 cells) where mean D < 0.

| Cut | n | Mean D (bp) | 99.5% CI | wk neg |
|---|---|---|---|---|
| Pooled |S|>=50 | 1005 | -8.6 | -21.2, +3.3 | 14/26 |
| Pooled |S|>=100 | 744 | -8.9 | -26.6, +6.4 | 15/26 |
| S tercile 1 (big down) | 336 | +2.5 | -12.8, +19.8 | 11/21 |
| S tercile 2 (middle) | 335 | -10.7 | -22.9, -0.3 | 15/26 |
| S tercile 3 (big up) | 334 | -17.8 | -49.6, +10.9 | 14/22 |
| |S| small | 336 | -5.4 | -15.7, +3.5 | 15/26 |
| |S| mid | 335 | -15.7 | -31.3, -1.5 | 19/26 |
| |S| large | 334 | -4.8 | -36.9, +17.9 | 14/24 |
| Liquidity low (<=100 trades in T-30 candle) | 337 | -16.0 | -32.4, -2.4 | 18/26 |
| Liquidity mid | 334 | -13.4 | -29.8, +1.1 | 17/26 |
| Liquidity high (>517 trades) | 334 | +3.6 | -15.6, +22.2 | 9/26 |
| Lateness early | 336 | -13.8 | -40.6, +10.5 | 11/26 |
| Lateness mid | 335 | -2.3 | -16.2, +10.0 | 15/25 |
| Lateness late | 334 | -9.8 | -31.2, +9.6 | 13/24 |
Slope of R = O - S on S: b = -0.017 (99.5% CI -0.071 to +0.034); b x median |S| = -2.8 bp. No size-dependent reversion.

Decision rule outcome: pooled and slope are null. Two cells of 12 formally meet the locked rule (|S| mid: -15.7 bp, 19/26 weekends; liquidity low: -16.0 bp, 18/26 weekends), each only about 1 bp above the 14.8 bp hurdle, with CIs whose upper end is only 1.5-2.4 bp from zero. The direction is mild reversion (open falls back toward Friday close), not overshoot. Liquidity-low cells are the thin perps, where 12 bp is probably too small a cost, and their mean funding-adjusted hurdle is 18 bp. Net of cost, about zero. Not tradable; at most it justifies a forward check on 21-23 Nov live data with ask/bid entry. Weekends and symbols overlap within a cell, so the cell CIs may still be optimistic.
Limits: candle close as mid, no spreads, Yahoo daily bars, 1 h candles.
