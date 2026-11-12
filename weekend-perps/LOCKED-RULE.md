# Weekend / out-of-hours perp test: LOCKED RULE (12 Nov 2026, written before any data)

Question: does a weekend perp price on an index or single stock predict the next cash open by MORE than spread + funding, with usable size?
Data only. No accounts, no orders, no keys. Read public market data only.

## Universe (fixed now)
Indices first: Hang Seng, Nikkei 225, S&P 500, Nasdaq 100. Then single stocks: Samsung, SK Hynix, plus the 5 highest-volume US single-stock perps found on the venue.
Venues: Hyperliquid HIP-3 dexes (public info API). Others added only if public API is reachable from the server.
Symbols with no live perp are recorded as "no market" (no substitution).

## Sampling
Logger polls every 60 s, all weekend-window symbols: mark, oracle, funding, open interest, day volume, top-of-book bid/ask (L2). Raw files kept, not committed.
Reference: official Friday cash close and next cash open per underlying (fetched later from an independent source, never from the venue).

## Signal (one definition, no variants)
S = (perp mid at T-30min before the cash open  -  Friday cash close) / Friday close, in bp.
T = official cash open of that underlying (HSI 01:15Z, Nikkei 00:00Z, US 14:30Z).
Outcome O = (Monday cash open - Friday close) / Friday close.
Primary bucket: |S| >= 100 bp. Secondary (reported, but counted in the variant correction): |S| >= 50 bp.

## Metrics, all reported
1. Direction hit rate in primary bucket vs 50% (binomial), clustered by weekend (one weekend = one unit across symbols).
2. Median absolute error of perp-implied open vs Friday-close-as-forecast. Improvement in bp.
3. Cost hurdle: median quoted half-spread at T-30min plus weekend funding paid, in bp. Edge only counts if median |S| captured exceeds this hurdle.
4. Matched placebo: random sign with the same |S| distribution; z of real vs placebo.
5. Top-3 weekend concentration of any P&L. Variant-count correction (2 buckets x symbols).
6. Size: median top-of-book USD depth at T-30min and weekend volume. Report capacity as $/day only from depth x frequency, never from first-print P&L.

## Pass / fail (locked)
PASS needs ALL: >= 20 weekends-with-signal in the primary bucket (else "unknown, N too small"), hit rate >= 70% with lower 95% bound > 55%, mean captured move > 2x cost hurdle, placebo z >= 2, no weekend > 40% of total.
Otherwise report "unknown" (N too small) or "fail". Never "promising".

## Honest timing
Live weekend data accrues 1 weekend per 7 days. 20 weekends = ~5 months. To avoid waiting: Step 0 backfill from venue historical candles (if available) for the same signal, clearly labelled backfill, same rule. Forward test confirms.
