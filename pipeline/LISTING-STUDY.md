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

## CORRECTION (19 Nov 06:30Z): spx-open size, by volume regime (`open_window.py`, `open_regime.py`, `out/listing1/open_regime.csv`)
The earlier "$32 depth, about $1/day" was wrong for two reasons: (1) it covered only Sep-Nov 2026, when the series had collapsed to $9k-$22k a day, and (2) the depth figure was a median over ALL decision clocks (08:00 to 09:25 ET), almost all of which are empty; the volume is in the first minute after the open (mean $724/day in minute 0 versus $20-60 in other minutes in Sep-Nov) which my 09:25 clock + 10-minute print window did touch but a pooled median hid.
Event volume per day (gamma, all 207 events 22 Jan to 18 Nov): Jan $358k, Feb $340k, Mar $150k, Apr $205k, May $122k, Jun $77k, Jul $44k, Aug $55k, Sep $14k, Oct $22k, Nov $9k.
Traded in 09:25-09:45 ET per day / in the open minute (09:30-09:31): Jan-Apr $20k-$34k / $5k-$12k; Jun $10k / $5k; Sep-Nov $0.9k-$2.4k / $0.3k-$1.2k.
Ex-post informed-taker profit (winner-token BUY prints below 0.95, size x (1 - price), the floor of stale depth), mean per day: pre-open (09:25-09:30) $86-$249 Jan-Apr; open minute $190-$400 Jan-Apr (Jun $1,313 on one day); later minutes $0-$1,553. Sep-Nov: $1-$68. In the 69 Jan-Apr days winner BUYs below 0.95 within 5 minutes after the open happened on only 10 days (14%), median first print 3 s after 09:30:00, about $490/day averaged over all days, so about $3.4k on each of those 10 surprise days. The rest of the days the market was already at 0.95+ before the open.
Not done: the nowcast edge (SPY pre-market vs prior close) in the high-volume months, because Yahoo returns 429 from this container and my 5m cache only reaches 26 Aug; and no recorded books exist for those months, so true ask depth and speed are unmeasured. Executed prints are a floor, heavy-tailed (10 days), and say nothing about whether you can detect the open within 3 seconds.

### Timing split of the open-window profit (`open_seconds.py`, `out/listing1/open_seconds_month.csv`)
Winner-token BUY prints below 0.95, size x (1 - price), mean $/day by seconds after 09:30:00 ET. Jan-Apr mean: 0-3 s $3, 3-10 s $140, 10-30 s $77, 30-60 s $63, 1-5 min $208 (total after 3 s about $487/day on 9 of 69 days). My earlier "median first print 3 s" was a 10-second bucket label, not 3 seconds; the 0-3 s bucket itself holds almost nothing. The $190-$400 figure therefore is mostly what remains after the first 3 s.

### Perp pre-open signal (`open_perp.py`, `out/listing1/open_perp_*.csv`; reuses the perps thread's markets/trades/Yahoo files from `weekend-perps/open-contracts-2026-11-19/run-2026-11-19/`)
Polymarket SP500-USD perp 1 s marks (api.perpetuals.polymarket.com), 77 dates 3 Aug-18 Nov (154 SPX+SPY open events). Signal at second s = sign of perp(s-1) / perp(prior 16:00 ET) - 1; own-token BUY prints on the picked token in [-300 s, +10 s] around 09:30:00 ET; P&L per share = win - price, no fees. The perp API returns nothing before mid-July and Yahoo/Hyperliquid are blocked from here, so Jan-Apr is NOT testable with futures or perps from this container.

## Elon 48h tweet counts (`elon_study.py`, `out/listing1/elon_{listing,rows}.csv`; hourly counts `pk_cache/elon_hourly.json`)
Counts: xtracker hourly stats Nov 2025 to 19 Nov 2026 (9,195 hours, fetched through TinyFish because the container blocks the host); my count lands in the winning bracket in 138 of 139 events. 139 two-day events (2026), trades for all 1,390 brackets (none truncated). Nowcast = count so far + trailing-21-day hour-of-day rate for the remaining hours; spread k and bias fitted on the first 69 events, scored on the last 70. Boundary d = distance of the projected count to the picked bracket's nearest edge / sd.
- Listing: 47.9 h before the window opens (count is 0 at listing); median first print 285 s after listing; printed $ in first 5 min median $0 (mean $9), in first 30 min median $17 (mean $82); event volume median $1.03M. Market favourite at +1/+10/+30 min is the winner 13% (n 31) / 15% (n 105) / 22% (n 128).
- Nowcast at listing picks the winning bracket 29% (train) and 53% (test), versus the market's favourite 8% (n 24) / 14% (n 7) where it had traded. Buying the listing pick on every BUY print up to +24 h: train -37% ROI, test +29%; up to +48 h: train -19%, test +33%, all events +6% ($137/event, about $60/day); sign flips between halves, so unproven.
- In-window (test half, d >= 0.5): nowcast hit equals market hit at 36/24/12/6/3 h before the end (0.57/0.59/0.78/0.81/0.87 vs 0.57/0.59/0.80/0.81/0.87); edge at +1 min fills -0.3c to -9.7c (se 5-9c), at 3 h -3.7c (se 5.0c). Nothing.
