# LOCKED RULE: commodity / FX / index perps vs the Sunday futures and FX reopen, and weekday tracking error (16 Nov 2026, written before any number was computed)

Origin: Nick, 16 Nov 15:09Z: small-open-interest perps (e.g. copper) cannot track the real price accurately; CME/COMEX futures close Friday 5pm to Sunday 6pm ET and FX is shut over the weekend, so the earlier "they trade through the weekend" exclusion was wrong for the reference.

## Universe (fixed)
Hyperliquid builder-dex perps (xyz and flx) and Polymarket perps in the commodity/FX/rates/vol group, paired with a Yahoo 1 h reference:
xyz: GOLD GC=F, SILVER SI=F, COPPER HG=F, PLATINUM PL=F, PALLADIUM PA=F, CL CL=F, BRENTOIL BZ=F, NATGAS NG=F, CORN ZC=F, WHEAT ZW=F, ALUMINIUM ALI=F, EUR EURUSD=X, JPY JPY=X, GBP GBPUSD=X, DXY DX-Y.NYB.
flx: OIL CL=F, GAS NG=F, COPPER HG=F, GOLD GC=F, SILVER SI=F, PLATINUM PL=F, PALLADIUM PA=F.
Polymarket: GOLD-USD GC=F, SILVER-USD SI=F, WTIOIL-USD CL=F, BRENTOIL-USD BZ=F.
Dropped before any computation (no usable hourly reference): VIX, VOL, KRW, H100, URANIUM, TTF, any symbol Yahoo returns nothing for. Orientation (price or inverse, e.g. JPY) is fixed by whichever of x1 or 1/x is closer to the reference at the first common hour; no outcome is looked at.
Open interest: from metaAndAssetCtxs (Hyperliquid) and /v1/info/tickers (Polymarket) at 16 Nov ~15:30Z, in USD (units x mark). Symbols are ranked by it. Reported as a snapshot, not history.

## Weekend test
A reopen = a gap of more than 36 h between consecutive Yahoo 1 h bars of the reference. F = close of the last bar before the gap; T = start of the first bar after it; O = open of that bar. S = (perp 1 h candle close at or before T-30 min - F) / F (bp), O = (O - F) / F. R = O - S. D = sign(S) x R (positive = reopen went beyond the perp, negative = reopen fell back toward Friday close). |R| is the weekend tracking error.
Per symbol: n cells, median |R|, median |S|, mean D with 95% weekend-cluster bootstrap CI (10,000 resamples, seed 1), and slope of R on S. A cell counts for the D mean only if |S| >= 50 bp.
## Weekday tracking error
For every Yahoo 1 h bar Monday-Friday that has a Hyperliquid/Polymarket 1 h candle at the same start time, excluding the first 2 h after any reference gap > 2 h and bars with zero reference volume where volume is reported: e = perp (close/open - 1) - reference (close/open - 1) in bp. Per symbol: median |e|, 90th percentile |e|, correlation of the two hourly returns. Returns, not levels, so front-month rolls do not enter.
## Classification (applied mechanically)
"Poor tracker" = median weekday |e| > 15 bp OR correlation < 0.9. "Weekend gap poor" = median |R| > 25 bp. Nick's claim (small OI tracks badly) is tested by the rank correlation (Spearman) between OI and median weekday |e|, reported with its n.
Nothing here is an edge claim; it says which perps can be trusted as a signal source at all. No definition or threshold may change after the first number is seen.
