# Weekend perps: locked test on backfill (16 Nov 2026)

Rule: weekend-perps/LOCKED-RULE.md incl. Amendment 2 (implementation locked before any result, PR #358). Data and scripts: weekend-perps/backfill-2026-11-16/. Confidence this report is right: 8/10 (audited sample matched; the doubt is the candle-close proxy for mid and 7 symbols only).

## What was tested
Hyperliquid xyz perps (JP225, SP500, XYZ100, NVDA, SNDK, MU, AMD, GOOGL) against Yahoo Friday close and Monday open, 22 Apr - 16 Nov 2026 (the venue keeps 1 h candles only back to 22 Apr). 201 symbol-weekends, 30 weekends (38 holiday cells dropped, Samsung/Hynix/KOSPI200 excluded, Hang Seng has no perp: "no market").

## Locked-rule numbers (primary bucket |S| >= 100 bp)
| Check | Result | Needs |
|---|---|---|
| Weekends with a signal | 27 | >= 20 |
| Signals / hits | 100 / 100 (95% CI by weekend bootstrap 1.00-1.00) | >= 70%, lower bound > 55% |
| Mean captured move C = sign(S) x O | +265 bp (median +196) | > 2x hurdle |
| Cost hurdle (12 bp round trip + funding) | median 16.4 bp | |
| Placebo z (sign shuffle) | 8.1 | >= 2 |
| Largest weekend share of total C | 10.2% (top 3: 28.5%) | <= 40% |
Every locked criterion is met on the backfill, so the Step 1 verdict is PROVISIONAL PASS (backfill only; the rule says forward data must confirm; delayed entry and far-side-of-book cannot be computed from candles). Secondary bucket (>= 50 bp): 141/143 hits.
Independent audit (random sample of 12 cells across the whole history, re-derived from the public APIs by a separate agent that was not shown my numbers): 12/12 match on S and O to 0.1 bp, no lookahead.

## What it means: not an edge
The rule itself says a perp cannot capture its own prediction: S is just the perp's price, and it predicts the open because it is the price discovery. What is left after the perp has moved is the real question:
- Slope of O on S (all 201 cells): 1.006, 95% CI 0.94 - 1.07. The perp is an unbiased forecast of the open.
- Residual after the perp has moved, C2 = sign(S) x (O - S), primary bucket: mean -3.5 bp, median +1.9, 95% CI -22.6 to +15.4 bp. That is zero and below the 16 bp hurdle.
- JP225 alone (n = 10): C2 mean -112 bp, but its signal is 60 min stale (hourly candles) and n is tiny. Not interpreted.
Step 2 (a lagging instrument) is untested: Polymarket perps are within a median 2.8 bp (p90 7 bp) of Hyperliquid at T-30 (98 cells, 14 weekends), so Polymarket is not lagging.

## Exploratory, NOT a locked result: post-open continuation on Polymarket perps
Polymarket perp history is public back to Aug 2026 (mark-history 1 s, klines, trades, funding). Same primary bucket on the PM mark (44 signals, 12 weekends), entry at the mark at T-29 min, no spread or slippage, exit at the PM mark:
| Exit | Mean | Median | 95% CI by weekend | Positive |
|---|---|---|---|---|
| T (cash open) | +20.0 bp | +15.3 | -4.2 to +45.8 | 66% |
| T + 5 min | +58.8 bp | +63.7 | +17.6 to +106.6 | 73% |
Two exits were tried after seeing nothing but this table, so this is a forking path; n = 44 cells over 12 weekends; entry uses the mark, not the ask. It suggests the perp keeps moving in the weekend direction for minutes after the cash open. Not weekend-specific by construction, and not tested. Proposed next step: write a new locked rule (single exit, ask/bid entry, includes weekday opens as a placebo) before looking at any further data, test it on the live logger data from 21-23 Nov plus Aug-Nov history not yet pulled.

## Limits
Candle close is a trade price, not a mid. Historical spread is unavailable (hurdle uses 12 bp). Today's top-volume US names were chosen with today's volume, so they are volatile survivors. 1 h candles make JP225's signal 30 min older than the rule's T-30. PM history only from Aug; I did not pull PM trades.
