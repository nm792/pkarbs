# Daily series: listing path, nowcast and boundary rule, printed depth (19 Nov 2026)

Code: `listing_study.py` (Up/Down series), `listing_brackets.py` (bracket series), tests `tests/test_listing.py` (nowcast cannot see a bar before it has ended). Outputs: `out/listing1/{rows,listing,brackets}.json`, `table.csv`. Inputs: 440 Up/Down markets ending 2 Sep to 18 Nov 2026 (52-54 session days per series), gamma events cache, CLOB `prices-history` fidelity 1 minute (own token), data-api trades (cache), Yahoo 5m bars (SPY with pre-market for spx-open, ^GSPC, ^DJI, ^RUT, META, NVDA, PLTR). Base commit bc38889863 plus this change.

## Method
Nowcast = sign of (last 5-minute bar ended at or before t) / (prior regular-session close) - 1. Boundary rule: z = |return| / daily sigma (previous 20 days), trade when z >= 0.5. Decision clocks 08:00, 09:00, 09:25, 10:00 ... 15:00 ET (spx-open only before 09:30). Fill = the earliest BUY print of the picked token's OWN book at or after t+1 min (or t+10 min), within 15 min; never 1 minus the other side. Edge per share = win - fill. Yahoo-derived outcome agreed with the resolved outcome in 96% (spx-open) to 100% of days; disagreeing days dropped.

## Result: ranked by edge at +1 min (n = decisions with a fill)
| series | listed (UTC) | first print after listing (median) | price at +30 min (own Up prints) | printed $ in first 30 min | nowcast hit | market favourite hit at t | edge/share at +1 min (+- se, n) | edge at +10 min | printed BUY depth on the picked token in 10 min (median) |
|---|---|---|---|---|---|---|---|---|---|
| spx-open | 12:00 | 8.7 h | 0.54 | $0 | 94.2% | 92.9% | +3.4c +- 1.4c (108) | +2.5c +- 1.8c (68) | $32 |
| meta | 12:00 | 9.3 h | 0.50 | $0 | 83.0% | 83.9% | +2.4c +- 2.9c (142) | +2.7c +- 3.1c | $0 |
| nvda | 12:00 | 9.0 h | 0.51 | $0 | 85.8% | 85.2% | +2.0c +- 2.5c (173) | +3.0c +- 2.5c | $0 |
| spx close | 12:00 | 6.8 h | 0.51 | $0 | 89.0% | 88.7% | +1.5c +- 2.2c (219) | +0.1c +- 2.3c | $20 |
| pltr | 12:00 | 9.4 h | 0.51 | $0 | 80.0% | 80.5% | +0.9c +- 3.7c (96) | +2.5c +- 4.1c | $0 |
| spy close | 12:00 | 9.1 h | 0.51 | $0 | 85.3% | 85.5% | -0.7c +- 2.4c (241) | +0.7c +- 2.3c | $0 |
| russell 2000 | 12:00 | 25.6 h | 0.50 | $0 | 88.3% | 87.0% | -2.0c +- 4.7c (62) | +3.2c +- 4.1c | $0 |
| dow | 12:00 | 18.5 h | 0.50 | $0 | 84.9% | 82.7% | -6.0c +- 5.0c (66) | -4.9c +- 4.8c | $0 |

Pooled over the 8 series and all clocks: the nowcast picks the same side as the market favourite in 97.6% of 3,048 decisions; the 74 where they differ were won by the nowcast 56.8% of the time (not distinguishable from 50%); pooled edge at +1 min +0.7c +- 1.0c (n 1,107), at +10 min +1.3c +- 1.1c (n 1,018). Only spx-open is above 2 standard errors (p about 0.02 before correcting for eight series, about 0.15 after), and it is tiny in size: $32 median printed depth per decision means about $1 per day.

## What this means (not a fail, a different shape from gas)
- **None of these is a listing-time contract.** They list at 08:00 ET the day before, sit at 0.50 with no print for 7 to 25 hours, and the outcome is next day's price move, which nobody can know at listing. Gas works because the input (AAA at 10:00 ET) is already published when the event lists; here the input does not exist yet.
- **The repricing happens during the next session, and the market is already on the nowcast.** Market favourite hit rate equals nowcast hit rate at every clock from 08:00 ET (e.g. spx-open 09:25 ET: both 98.1%). The jump-screen clock (spx-open 13:40Z, spx close 19:30-20:30Z) is the sharp pre-open and late-session moves in the underlying, and the market follows within the 1-minute resolution I can see.
- Size is the limit: printed BUY depth is $0 in the median 10-minute window for six of eight series.

## Bracket series (first 30 min after listing, 20 latest events each, YES tokens)
| series | first print (median) | printed $ in first 30 min (median / mean) | favourite price at +30 min | favourite at +30 min is the winner |
|---|---|---|---|---|
| us-gas-price-daily | 23.6 min | $1.3 / $39.7 | 0.69 | 16 of 20 (80%) |
| spy-daily-close-uo | 11.4 min | $0 / $14 | 0.85 | 80% (trivial: favourite is a deep strike) |
| wti-daily-close-uo | 29.5 min | $0 / $0.4 | 0.70 | 90% (same) |
| elon-tweets-48h | 21.7 min | $0 / $0.9 | 0.50 | 20% (4 of 20) |
| trump-truth-social | none in 30 min | $0 | 0.37 | 15% (3 of 20) |
Gas in this table reproduces the main handler's listing finding (favourite right 80% at +30 min, mean price 0.69). For the tweet counters the input (xtracker post count) is a live counter that moves during the window, so the listing-time nowcast is a rate forecast, and xtracker.polymarket.com is blocked from this container (no connection), so I could not build the nowcast or test it. That is a concrete ask only if wanted: the server agent can poll xtracker and the recorder can log it.

## Limits
- Fills are the earliest BUY print, not a resting-book measurement; no historical books exist. Depth is printed, so a floor.
- Edge estimates carry 1.4c to 5c standard errors on 52-54 days; eight series times ten clocks were looked at; nothing is corrected except where stated.
- Yahoo prices are a proxy for the resolution source (Pyth or official index); 0 to 4% of days disagreed and were dropped.
- Gold, natural gas and WTI up/down not tested (Pyth continuous-close definition not reproducible from Yahoo futures bars).
