# LOCKED RULE: does the Monday open systematically overshoot or undershoot the weekend perp? (16 Nov 2026, written before any number was computed)

Origin: Nick, 16 Nov 14:59Z: "nothing says the two prices must converge when only one of them has price discovery." The earlier test only showed the perp predicts the open direction; this asks whether the open moves *past* or *short of* the perp's last price in a predictable way.

## Data (fixed)
All rows already produced by the backfills: weekend-perps/backfill-2026-11-16/rows.json (8 symbols) and the 54-symbol extension (/tmp/wp2/rows.json, copied to weekend-perps/backfill-2026-11-16/rows_ext.json). 62 symbols, USD-quoted, Fri close to Mon open cells. Non-USD names already dropped. No rows added or removed after seeing results.

## Definitions
S = (perp price at T-30 min - Friday cash close) / Friday close (bp). O = (Monday open - Friday close) / Friday close (bp). Residual R = O - S (bp). Directional residual D = sign(S) x R (positive = the open moved further in the weekend direction = overshoot; negative = open fell back toward Friday close = undershoot / reversion). Hurdle = median 12 bp + funding (as in Amendment 2), about 15 bp.
Sample for all tests: rows with |S| >= 50 bp (the secondary bucket, for sample size); the |S| >= 100 bp bucket is reported alongside.

## Tests (all run once, all reported)
1. Pooled mean D, with 95% CI by weekend-cluster bootstrap (10,000 resamples, seed 1).
2. Terciles of signed S (big down / middle / big up): mean D per tercile.
3. Terciles of |S|: mean D per tercile.
4. Liquidity: terciles of the number of trades in the T-30 candle (n_trades): mean D per tercile.
5. Lateness: L = (P - P12) / (P - F), the share of the weekend move that happened in the last 12 hours before T-30 (P12 = close of the last 1 h candle ending at or before T-12 h-30 min; rows without it are dropped, count reported). Terciles of L: mean D per tercile.
6. Regression R = a + b x S (OLS), slope b with weekend-cluster bootstrap 95% CI. b > 0 means overshoot grows with the weekend move; b < 0 means reversion.
All tercile cut points are computed on the pooled sample (not per symbol).

## Decision rule
12 tests are looked at (pooled, 9 tercile cells, slope; the |S|>=100 bucket is a repeat, not extra). A cell counts as a finding only if its 99.5% weekend-cluster bootstrap interval (Bonferroni-style, about 0.05/12... rounded to 0.5% tails) excludes zero AND |mean D| > hurdle (about 15 bp) AND the sign matches in at least 2/3 of the weekends where the cell has at least 3 rows. The slope counts only if its 99.5% interval excludes zero and |b x median |S|| > hurdle. Anything else is reported as "no systematic over/undershoot".
A pass here is still NOT tradable: it would only justify a forward test on the live logger data (21-23 Nov) with ask/bid entry. No result from this test may be called an edge.
No cuts, thresholds or definitions may be changed after the first number is seen; any new idea needs a new rule file.
