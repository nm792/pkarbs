## Contract
Rule: If average regular gas prices for United States are strictly greater than $4.0500 on Nov 10, 2026 according to AAA, then the market resolves to Yes.
Opens ~13:00Z on D-1, closes 04:59Z on D (midnight US Eastern), settles on AAA's published D value ~12:15Z on D. Ladder of ~17 'above X' strikes in 0.5c steps around the expected value; 255 events in history (18-US .. NOV10).

Analysed 21 random events, 360 strikes (hour-1 favourite = side priced >=50c).

Favourite wins 93.6% of strikes; underdog wins 6.4% (23 cases).

## Underdog cost vs win rate at hour 1 (underdog side ask)
| underdog ask | strikes | underdog wins | cost | gap (win - cost, before fee) |
|---|---:|---:|---:|---:|
| 0-3c | 193 | 0.0% | 1.6c | -1.6c |
| 3-10c | 85 | 1.2% | 5.4c | -4.2c |
| 10-25c | 47 | 14.9% | 16.8c | -1.9c |
| 25-50c | 30 | 43.3% | 39.0c | +4.3c |

## Underdog-win cases: what separated them
- Actual AAA move (cents vs previous day) across analysed events: mean -0.51c, sd 1.70c.
- Underdog wins happen at strikes the actual value finished close to: median |actual - strike| = 0.35c for underdog wins vs 2.33c for favourite wins.
- Share of underdog wins where AAA finished within 1c of the strike: 91% (all strikes within 1c: 23%).
- Flip timing (hours after open until price stayed on the winning side): median 8h of a ~13h life; 26% flipped after 70% of life.

| event | strike | AAA at open (prev day) | AAA actual | move | strike - AAA open | fav ask @open | underdog ask @open | flip (h of life) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| NOV03 | 4.155 | 4.169 | 4.149 | -2.0c | -1.4c | 63c | 38c | 5 of 15 |
| NOV03 | 4.150 | 4.169 | 4.149 | -2.0c | -1.9c | 81c | 21c | 10 of 15 |
| OCT05 | 4.365 | 4.370 | 4.365 | -0.4c | -0.5c | 58c | 45c | 15 of 15 |
| OCT06 | 4.365 | 4.365 | 4.369 | +0.3c | -0.0c | 97c | 6c | 12 of 15 |
| OCT06 | 4.360 | 4.365 | 4.369 | +0.3c | -0.5c | 94c | 10c | 4 of 15 |
| OCT07 | 4.370 | 4.369 | 4.367 | -0.2c | +0.2c | 62c | 39c | 8 of 15 |
| OCT14 | 4.335 | 4.341 | 4.333 | -0.8c | -0.6c | 73c | 31c | 7 of 15 |
| OCT23 | 4.290 | 4.270 | 4.293 | +2.2c | +2.0c | 53c | 49c | 2 of 15 |
| OCT24 | 4.300 | 4.293 | 4.296 | +0.3c | +0.7c | 66c | 35c | 8 of 15 |
| OCT27 | 4.265 | 4.286 | 4.266 | -2.0c | -2.1c | 80c | 24c | 5 of 15 |
| OCT28 | 4.250 | 4.266 | 4.247 | -1.9c | -1.6c | 63c | 38c | 8 of 15 |
| OCT29 | 4.230 | 4.247 | 4.226 | -2.1c | -1.7c | 83c | 20c | 4 of 15 |
| OCT30 | 4.205 | 4.226 | 4.205 | -2.1c | -2.1c | 53c | 48c | 2 of 15 |
| SEP06 | 4.145 | 4.146 | 4.147 | +0.1c | -0.1c | 59c | 45c | 9 of 15 |
| SEP08 | 4.155 | 4.151 | 4.151 | +0.1c | +0.5c | 78c | 28c | 14 of 15 |
| SEP16 | 4.365 | 4.329 | 4.367 | +3.8c | +3.6c | 91c | 23c | 13 of 15 |
| SEP16 | 4.360 | 4.329 | 4.367 | +3.8c | +3.1c | 86c | 17c | 4 of 15 |
| SEP16 | 4.355 | 4.329 | 4.367 | +3.8c | +2.6c | 72c | 52c | 3 of 15 |

## Is the ladder's centre biased vs a naive forecast?
- Market-implied median at open vs actual: mean error -0.04c, MAE 0.57c over 21 events.
- Naive 'yesterday + yesterday's move': MAE 0.92c over 21 events.
- RBOB/wholesale data was NOT tested (needs a futures series; not in this run).
