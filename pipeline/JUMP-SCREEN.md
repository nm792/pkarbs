# Late jump to the winner: screen and gas deep-dive (19 Nov 2026)

Re-centred on Nick's criteria (04:29Z): daily or more frequent, high volume, and late moves to the winner. The late move is the thing to exploit, not to predict from. Code `jumps.py` (screen), `forward/` (recorder), outputs `out/jumps1/`, gas details `out/gas_release.json`.

## What was wrong with the earlier screen (gas explicitly)
Gas (`us-gas-price-daily`, AAA national average, 6 brackets, one event per day) **was in the universe**: 34 events in the 30-day window, median event volume $3.2k, total $138k. It ranked low because (1) the late-move metric was measured at 60/15/5 min before the scheduled end (15:00Z) and gas converges 6 to 12 hours earlier, so it looked efficient at 0.98 by T-15; (2) the model panel used fixed decision hours before the end (10 min to 24 h), most of which fall after the gas release, and rows with fills at 0.99 were dropped (6 gas rows in 17,445); (3) volume is small (rank 28 of 69). The design gap is real: **anchor on the release clock time, not the scheduled end.**

## Gas: what the data show (`out/gas_release.json`, 34 events)
- Resolution rule (gamma event text): price displayed on gasprices.aaa.com at 10:00 AM ET on the date, provided "Price as of" is that date and "Yesterday Avg." is the previous date's price. So the trigger is AAA's page rolling to the new date.
- The winning bracket converges to >= 0.95 inside 03:00-11:00Z in 32 of 34 events; **median 07:39Z** (p10 03:15Z, p90 08:23Z), median price just before the converting print 0.93.
- Favourite is the winner 64% at 16:00Z the day before, 76% at 05:00-07:00Z (mean winner price about 0.80), **100% at 09:00Z (mean winner price 0.983)**. So the daily repricing Nick saw is the AAA update: the favourite at 07:00Z is wrong a quarter of the time, and by 09:00Z the market is exact.
- Money: informed-taker profit pool (winner BUY prints below 0.95 before conversion, size x (1 - price)) averages $33 per event, $1,105 in 30 days (about $37/day). That is what was actually executed, a floor for stale depth, not a ceiling.
- Live book now (19 Nov 04:34Z, `forward-data/gas_20261119.jsonl`): the winner bracket is already 0.994/0.998 with $90 of asks; the other five brackets ask 0.004 to 0.006. The release for 19 Nov had already happened before 04:34Z (p10 case).
- **Gas as it stands is small**: about $4.6k/day of total volume. It is real, daily and scheduled, but even full capture is tens of dollars a day unless the stale asks are far deeper than what traded, which only recorded books can show.

## Jump-to-winner ranking across 54 daily-or-faster series (`jumps.py`, 120 events per series, winning market only)
Definitions: T* = last winner print below 0.95 on the winning token's own prints; the move completes at the next print; pre-price = last print at least 20 min earlier; sharp = jump >= 0.30 from a pre-price <= 0.80; clock = UTC minute of the first departure; pool = size x (1 - price) of winner BUY prints at <= 0.90 during the move.

| series | ev/day | median event vol $ | sharp jump rate | median jump (pre to post) | duration min | converges before scheduled end (h) | modal UTC start (share of sharp) | informed-taker pool $/event | pool $/day |
|---|---|---|---|---|---|---|---|---|---|
| elon-tweets-48h | 0.43 | 1,027,257 | 17% (20/120) | 0.45 to 0.96 | 9.1 | 0.5 | 15:35 (45%) | 2621 | 189.8 |
| spx-daily-up-or-down | 0.68 | 94,786 | 17% (20/120) | 0.46 to 0.97 | 13.5 | 0.0 | 20:20 (60%) | 1497 | 170.9 |
| spx-open-daily-up-or-down | 0.69 | 36,940 | 16% (19/120) | 0.46 to 0.97 | 7.2 | 6.5 | 13:40 (84%) | 549 | 59.8 |
| dissent-at-fed-meeting | 0.02 | 81,537 | 91% (10/11) | 0.30 to 0.97 | 0.5 | -18.0 | 18:30 (90%) | 1007 | 22.1 |
| meta-daily-up-down | 0.68 | 4,072 | 24% (29/119) | 0.49 to 0.96 | 7.9 | 0.0 | 19:30 (62%) | 129 | 21.6 |
| dow-jones-daily-up-or-down | 0.68 | 2,366 | 21% (25/119) | 0.39 to 0.97 | 0.0 | 0.0 | 20:20 (60%) | 141 | 20.2 |
| silver-up-or-down-1h | 13.39 | 0 | 38% (6/16) | 0.34 to 0.99 | 7.5 | 0.0 | 01:30 (17%) | 4 | 17.8 |
| spy-daily-close-uo | 0.69 | 36,660 | 12% (14/119) | 0.60 to 0.96 | 12.0 | 0.0 | 19:30 (79%) | 180 | 14.5 |
| gold-up-or-down-15m | 53.26 | 255 | 3% (3/92) | 0.51 to 1.00 | 2.1 | -0.0 | 00:00 (67%) | 8 | 14.0 |
| nvda-daily-up-down | 0.68 | 5,345 | 13% (16/120) | 0.37 to 0.97 | 7.6 | 0.0 | 19:40 (50%) | 147 | 13.4 |
| wti-daily-close-uo | 0.68 | 39,575 | 19% (22/115) | 0.53 to 0.99 | 5.6 | 0.2 | 20:30 (77%) | 91 | 11.8 |
| trump-truth-social | 0.29 | 86,271 | 22% (18/80) | 0.39 to 0.98 | 6.5 | 1.0 | 15:00 (33%) | 165 | 10.8 |
| spy-daily-up-or-down | 0.69 | 39,492 | 7% (8/118) | 0.36 to 0.97 | 2.1 | 0.0 | 19:30 (100%) | 205 | 9.6 |
| gold-daily-up-or-down | 0.69 | 9,586 | 8% (10/120) | 0.55 to 0.96 | 6.1 | 0.2 | 20:30 (60%) | 139 | 8.0 |
| russell-2000-daily-up-or-down | 0.68 | 2,228 | 22% (24/110) | 0.48 to 0.98 | 0.0 | 0.1 | 20:40 (50%) | 50 | 7.5 |
| pltr-daily-up-or-down | 0.68 | 2,743 | 12% (15/120) | 0.53 to 0.95 | 4.9 | 0.0 | 20:30 (47%) | 86 | 7.4 |
| us-gas-price-daily | 1.00 | 3,216 | 18% (6/34) | 0.46 to 0.98 | 3.1 | 6.5 | 07:00 (50%) | 6 | 1.1 |
| natural-gas-daily-up-or-down | 0.68 | 3,893 | 19% (19/101) | 0.48 to 0.99 | 0.0 | 0.1 | 20:30 (58%) | 1 | 0.1 |

Reading it:
- **SPX/SPY "open" markets are the cleanest scheduled release**: spx-open converges at 13:40Z (84% of sharp jumps within 30 min of that time; this is the 09:30 ET cash open in summer, 14:30Z in winter), about 7 minutes, ~6.5 hours before the scheduled end. Pool $60/day.
- **Elon 48h tweets**: biggest pool ($190/day, event volume $1.0M) but the trigger is the tweet counter crossing a bracket at no fixed clock time; modal 15:35Z share only 45%.
- **SPX/SPY/stock close markets** converge at 19:30-20:30Z, i.e. during the last hour of trading, pool $10-170/day; no scheduled release, the information is the live index.
- Gas, natural gas and the others have sharp-jump rates of 7% to 26%: most of the time the winner is already the favourite before the final move; the jump is large only when the favourite was wrong.

## Triggers and how to measure speed and depth
- Gas: AAA page flip ("Price as of"), needs a poller on gasprices.aaa.com (this environment cannot reach it: egress proxy refuses the host). Spx-open: official open print at 09:30 ET (Yahoo ^GSPC 1 m is reachable). Elon: live post counter (xtracker), not yet handled.
- `forward/recorder.py` (tests in `tests/test_forward.py`, 23 tests pass overall) records, every 20 s inside the window, own-token books for every bracket plus the external source (AAA page or Yahoo SPX), so repricing lag and ask depth at the release can be read directly. No orders. A copy is running here (PM books and Yahoo only) writing to `/mnt/project-files/pipeline/forward-data/`; it dies with this container, so a durable run needs the server agent: `python3 pipeline/forward/recorder.py --out <volume>/forward --jobs gas,spxopen`, with egress to gasprices.aaa.com, clob.polymarket.com, gamma-api.polymarket.com and query1.finance.yahoo.com.

## Limits
- Ex-post pools are executed volume, not available depth; no historical books exist for these series, so true stale-ask depth and speed are unmeasured until the recorder has run.
- 120 events per series (30 to 100 for tweets and gas); the sharp threshold (0.30 jump from <= 0.80) is a choice and hides small but frequent jumps such as gas 0.92 to 0.99.
- Gas release timing is inferred from Polymarket prints, not from AAA's own page.
- The 23 mined factors from the qlib stage did NOT survive a rerun of the same selection from scratch on all rows from 25 Mar 2026 (0 of 624 cells pass BH), so they are not robust to how rows are chosen; the requested frozen forward test is therefore not meaningful as specified and is not done. No pre-registered forward score exists yet for the 6 h and 1 h leads.
- Pool figures differ between the table (mean over sharp events found by the generic detector, gas $6/event) and the gas deep-dive ($32/event, release window 03-11Z on every event); the second is the more relevant for gas.
