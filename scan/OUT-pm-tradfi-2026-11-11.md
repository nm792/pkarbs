# Polymarket tradfi: direct search (last 60 days, crypto and 5/15-minute windows excluded)

| series (title pattern) | volume $/day | resolved markets (events) | winners measured | late share (>70% of life) | early-leader share (<=10%) | mean emergence |
|---|---:|---|---:|---:|---:|---:|
| S&P # (SPX) Up or Down on M? | $17,897 | 42 (42) | 22 | 41% | 5% | 0.57 |
| WTI Crude Oil (WTI) closes above ___ on M? | $10,866 | 462 (42) | 100 | 18% | 32% | 0.33 |
| S&P # (SPY) closes above ___ on M? | $10,367 | 462 (42) | 109 | 15% | 80% | 0.16 |
| SPY (SPY) Up or Down on M? | $7,497 | 42 (42) | 22 | 36% | 0% | 0.61 |
| S&P # (SPX) Opens Up or Down on M? | $6,109 | 42 (42) | 22 | 23% | 14% | 0.47 |

## Early leader: price vs win rate (favourite side at ask = mid + 1.5c slippage, + fee, hold to settlement; binary up/down series)
| series | checkpoint | half | markets | fav ask | win rate | gap net of fee (95% CI) | net/$ |
|---|---|---|---:|---:|---:|---|---:|
| S&P # (SPX) Up or Down on M? | first hour | train | 11 | 53.3c | 27.3% | -26.54c (-45.45, +1.32) | -49.33% |
| S&P # (SPX) Up or Down on M? | first hour | TEST | 11 | 55.7c | 63.6% | +7.28c (-24.40, +33.64) | +13.74% |
| S&P # (SPX) Up or Down on M? | 10% of life | train | 11 | 53.7c | 54.5% | +0.32c (-28.04, +28.37) | +1.97% |
| S&P # (SPX) Up or Down on M? | 10% of life | TEST | 11 | 55.8c | 63.6% | +7.23c (-20.53, +34.74) | +12.94% |
| S&P # (SPX) Up or Down on M? | 25% of life | train | 11 | 57.1c | 45.5% | -12.22c (-39.09, +16.50) | -23.80% |
| S&P # (SPX) Up or Down on M? | 25% of life | TEST | 11 | 58.6c | 45.5% | -13.75c (-39.70, +13.65) | -25.27% |
| WTI Crude Oil (WTI) closes above ___ on M? | first hour | train | 51 | 66.8c | 76.5% | +9.17c (-4.03, +20.55) | +19.63% |
| WTI Crude Oil (WTI) closes above ___ on M? | first hour | TEST | 49 | 67.8c | 67.3% | -0.91c (-13.08, +10.70) | -1.71% |
| WTI Crude Oil (WTI) closes above ___ on M? | 10% of life | train | 51 | 66.3c | 78.4% | +11.60c (+0.15, +21.99) | +21.82% |
| WTI Crude Oil (WTI) closes above ___ on M? | 10% of life | TEST | 49 | 64.2c | 63.3% | -1.37c (-14.06, +11.13) | -4.37% |
| WTI Crude Oil (WTI) closes above ___ on M? | 25% of life | train | 51 | 75.4c | 82.4% | +6.50c (-3.70, +16.76) | +12.25% |
| WTI Crude Oil (WTI) closes above ___ on M? | 25% of life | TEST | 49 | 70.5c | 71.4% | +0.49c (-11.43, +12.39) | +0.84% |
| S&P # (SPY) closes above ___ on M? | first hour | train | 56 | 87.7c | 91.1% | +3.21c (-2.69, +8.63) | +1.98% |
| S&P # (SPY) closes above ___ on M? | first hour | TEST | 53 | 81.7c | 69.8% | -12.26c (-24.63, -0.59) | -15.38% |
| S&P # (SPY) closes above ___ on M? | 10% of life | train | 56 | 90.7c | 96.4% | +5.59c (+1.14, +9.84) | +6.75% |
| S&P # (SPY) closes above ___ on M? | 10% of life | TEST | 53 | 85.2c | 73.6% | -12.00c (-23.92, -1.39) | -15.40% |
| S&P # (SPY) closes above ___ on M? | 25% of life | train | 56 | 90.2c | 92.9% | +2.48c (-3.87, +7.62) | +2.32% |
| S&P # (SPY) closes above ___ on M? | 25% of life | TEST | 53 | 85.2c | 75.5% | -10.04c (-21.44, -0.18) | -12.22% |
| SPY (SPY) Up or Down on M? | first hour | train | 11 | 54.8c | 45.5% | -9.89c (-41.31, +20.00) | -14.47% |
| SPY (SPY) Up or Down on M? | first hour | TEST | 11 | 54.2c | 45.5% | -9.40c (-36.50, +17.96) | -17.30% |
| SPY (SPY) Up or Down on M? | 10% of life | train | 11 | 53.0c | 27.3% | -26.22c (-45.50, +1.73) | -48.72% |
| SPY (SPY) Up or Down on M? | 10% of life | TEST | 11 | 54.2c | 45.5% | -9.40c (-36.95, +18.55) | -16.92% |
| SPY (SPY) Up or Down on M? | 25% of life | train | 11 | 56.3c | 45.5% | -11.36c (-39.54, +18.51) | -20.02% |
| SPY (SPY) Up or Down on M? | 25% of life | TEST | 11 | 59.1c | 54.5% | -5.15c (-34.44, +22.97) | -7.49% |
| S&P # (SPX) Opens Up or Down on M? | first hour | train | 11 | 59.4c | 45.5% | -14.43c (-41.91, +13.35) | -25.79% |
| S&P # (SPX) Opens Up or Down on M? | first hour | TEST | 11 | 56.3c | 45.5% | -11.41c (-40.85, +16.45) | -18.50% |
| S&P # (SPX) Opens Up or Down on M? | 10% of life | train | 11 | 57.6c | 54.5% | -3.62c (-30.85, +23.89) | -8.23% |
| S&P # (SPX) Opens Up or Down on M? | 10% of life | TEST | 11 | 59.1c | 63.6% | +3.96c (-25.43, +30.83) | +8.05% |
| S&P # (SPX) Opens Up or Down on M? | 25% of life | train | 11 | 58.6c | 54.5% | -4.57c (-30.62, +21.30) | -11.26% |
| S&P # (SPX) Opens Up or Down on M? | 25% of life | TEST | 11 | 62.2c | 72.7% | +9.91c (-18.46, +33.25) | +18.22% |
