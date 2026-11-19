# LOCKED RULE: Polymarket perps, drift after the cash open, tested on history with executable prices (16 Nov 2026, written before any number of this test was computed)

Origin: Nick, 16 Nov 15:09Z: "why would we not just check the history?" Replaces waiting for the 21-23 Nov logger data; that data is still used later as a forward check.
The earlier +20 bp (open) / +59 bp (T+5 min) numbers were exploratory on the mark price with two exits. They are NOT used here.

## Data (fixed)
Polymarket perps API (api.perpetuals.polymarket.com): /v1/info/mark-history (1 s), /v1/info/trades (taker side, price, timestamp, per instrument). History from 1 Aug 2026. Cash references: Yahoo daily bars (open timestamp = official cash open T, Friday/previous-day close F).
Instruments: Polymarket equity + index category perps with a US-listed Yahoo underlying: SP500 (^GSPC), NAS100 (^NDX), and every equity-category symbol with a plain US ticker (GOOG-USD = GOOG). Excluded: SKHY, SKHYNIX, SAMSUNG, CXMT, UNITREE, SPCX, CBRS, ANT (no clean listed reference), and any symbol for which Yahoo returns no data.
Cells: every Monday open from 3 Aug (weekend cells) and every Tuesday-Friday open (weekday placebo cells), excluding days whose previous Yahoo bar is not the previous trading day.

## Signal
S = (PM mark at T-30 min - F) / F in bp. A cell is a signal if |S| >= 100 bp (weekday placebo uses the same threshold against the previous day's cash close).

## Trade (one entry, one exit, no choices)
Entry: the first taker trade with side "long" (if S > 0) or "short" (if S < 0) with timestamp in [T-29 min, T-20 min]; entry price = that trade's price. That is a price someone actually paid to cross the spread.
Exit: the first taker trade of the opposite side (side "short" if S > 0, "long" if S < 0) with timestamp in [T+5 min, T+10 min]; exit price = that trade's price. Cells with no qualifying entry or exit trade are dropped and counted (a high drop share is itself reported).
Gross = sign(S) x (exit - entry) / entry (bp). Costs: taker fee 4 bp per side (equity category default from /v1/info/fees, no tier discounts, no fee overrides) = 8 bp round trip, plus funding accrued over the holding period if it can be read, else ignored and stated. Net = gross - costs.
Sizing and impact: not modelled; trade-size is reported (median trade quantity x price at entry and exit) so the capacity limit is visible.

## Tests
1. Weekend cells: mean net and median net, with 95% CI by weekend-cluster bootstrap (10,000 resamples, seed 1), % positive, n, number of weekends.
2. Weekday placebo cells: same numbers. Difference weekend minus weekday with a bootstrap CI over day-clusters.
3. Report by symbol group (index vs equity) and spread proxy (entry price vs the nearest opposite-side trade within 10 s).
## Decision rule
PASS only if all of: >= 30 weekend signals over >= 10 weekends; weekend mean net > 0 with the 95% CI lower bound > 0; weekend mean net exceeds the weekday placebo mean with the CI of the difference excluding 0; no single weekend contributes more than 40% of the total net. Otherwise "no drift after cost" (or "unknown" if the sample is short, and say what settles it). A PASS is not capacity: it only justifies a forward test on the 21-23 Nov live data.
No parameter above (windows, threshold, fee, instruments) may change after the first number is seen; any new idea needs a new rule file.
