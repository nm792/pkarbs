# Cheap gas signal test: does AAA's last change predict near-strike outcomes better than the market?
Near-strike = YES mid 25-75c at hour 1 after open, strikes within 3c of the prior-day AAA value. Signal = direction of AAA's last daily change (momentum). Gap = win rate - ask - fee. Placebo = random signal direction per event (2000 draws). Size = 10% of $ traded in the 2h after hour 1 (x0.5 taker-buy).

| series | half | strikes (events) | hit rate | market-implied | gap net of fee (95% CI) | net/$ | placebo z | size/strike | $/day | days |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| national daily | train | 51 (26) | 51.0% | 50.9% | -5.56c (-21.97, +10.75) | -8.8% | +0.0 | $53 | $1 | 28 |
| national daily | TEST | 47 (36) | 44.7% | 49.7% | -8.05c (-24.02, +10.46) | -10.9% | -0.5 | $185 | $16 | 37 |
| state CA | train | 58 (10) | 39.7% | 46.9% | -45.38c (-59.44, -32.27) | -56.1% | -1.0 | $13 | $-19 | 9 |
| state CA | TEST | 51 (22) | 39.2% | 43.7% | -32.64c (-49.85, -9.09) | -39.8% | -0.5 | $22 | $-14 | 29 |
| state TX | train | 62 (9) | 46.8% | 50.5% | -39.09c (-49.13, -30.99) | -48.3% | -0.6 | $0 | $-4 | 8 |
| state TX | TEST | 59 (25) | 45.8% | 47.8% | -24.66c (-38.29, -8.65) | -35.5% | -0.3 | $4 | $-7 | 30 |
| state FL | train | 61 (13) | 32.8% | 45.8% | -48.05c (-64.34, -23.24) | -61.5% | -1.2 | $10 | $-37 | 17 |
| state FL | TEST | 53 (13) | 60.4% | 55.0% | -18.72c (-41.78, +6.76) | -19.4% | +0.5 | $3 | $-6 | 17 |
| state NY | train | 41 (6) | 24.4% | 46.8% | -63.17c (-76.00, -53.48) | -74.1% | -2.2 | $4 | $-27 | 6 |
| state NY | TEST | 35 (18) | 22.9% | 43.8% | -50.20c (-66.30, -23.32) | -65.2% | -1.8 | $12 | $-4 | 32 |
