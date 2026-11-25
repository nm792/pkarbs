# Earnings-beat contracts: base rate and first screen (ledger L7, OPEN-ITEMS 26), 25 Nov 2026 09:30Z

Reviewer did this itself (the mentions thread's 08:00Z delivery never landed). Public data only; nothing traded. Screen on PRINTS, not on own-token asks: a SCREEN, not a result.

## Data
- `pull.py`: every closed Polymarket "X beats quarterly earnings?" market (gamma `tag_slug=earnings`, slug contains `quarterly-earnings`): **1,610 markets, Sep 2025 - Nov 2026, $21.8M total volume**; last 30 days 203 markets, $607K.
- `trades_jump.py`: every trade per market from Data API v2 `/v2/trades?condition=` (cursor pages; condition_id asserted on every row; a wrong id returns an error). YES price = price on the YES token, 1 - price on the NO token.
- Report time: gamma `startTime` is NOT the report time (89% of markets were already at 0-2c or 98-100c before it). So the report time J = the first trade after which every price stays >= 97c (YES won) or <= 3c (NO won). Pre-report price = the last trade at least 30 min before J, kept only if it is under 24 h old and between 3c and 97c. 1,562 markets have a J; 1,368 are usable.
- Fee: each market's own feeSchedule (rate 0.01 x p(1-p) taker where listed, else 0).

## Base rate
Beat (YES) rate **73.6%** on the 1,368 usable markets (73.4% on all 1,610); the mean pre-report price was 71.2c.

## Calibration (`calib.py`, output `calib.txt`)
| pre-report price | n | mean price | realised beat rate | diff (95% CI) |
|---|---|---|---|---|
| 0-20c | 94 | 11.8c | 23.4% | +11.6 +-8.6 |
| 20-40c | 119 | 29.2c | 36.1% | +7.0 +-8.6 |
| 40-50c | 65 | 44.3c | 52.3% | +8.0 +-12.1 |
| 50-60c | 76 | 55.0c | 60.5% | +5.5 +-11.0 |
| 60-70c | 120 | 64.6c | 69.2% | +4.5 +-8.3 |
| 70-80c | 168 | 74.9c | 76.2% | +1.3 +-6.4 |
| 80-90c | 286 | 85.0c | 85.3% | +0.3 +-4.1 |
| 90-100c | 440 | 93.5c | 92.5% | -1.0 +-2.5 |
Cheap YES is underpriced; favourites are fairly priced.

## First screen
- **Buy YES when the pre-report print is under 50c: n=278, +58.7% per $ staked after fee (bootstrap 95% CI +24.1% to +96.8%).**
- We ran a test where the prices are assumed correct and outcomes are redrawn from them (MC type 2, randomised data on the same markets): its 95th percentile is +22.1%, p < 0.0002. We also ran random-side trades on the same markets (MC type 1): 95th percentile +14.1%.
- Stability: earlier half +79.0% [+24.6, +140.6], later half +38.5% [-2.6, +85.5]. Weaker recently; CI touches 0.
- Other rules: buy YES >= 80c -0.5% [-3.0, +2.0]; buy NO < 20c -13.2% (the mirror loses, as expected).

## What it is not (yet)
- Prices are last PRINTS, not the YES token's own ask (SETTLED A1). A print may be a sale at the bid; the ask can be higher.
- Depth: median $376 traded in the 24 h before the report on these markets (p75 $1,148). Capacity is small per market; volume is spread over ~200 markets/month.
- J is inferred from prints; a late J could put post-report prints in the "pre" price (that would shrink, not create, the edge on cheap YES that won).

## Host
This screen ran in the session container on public data. Under R-039 (Nick 22 Nov) backtests run on Prime, so the screen is to be re-run there from the pinned SHA before any number is used beyond triage; the own-ask scoring (next step 1) runs on Prime.

## Next
1. Own-token asks: P121 already records earnings-beat books (family tag `earnings_beat`) since 23 Nov. Score this rule against the YES token's own asks at each pre-report snapshot, and measure $ depth at those asks (IT read-only row, with P147).
2. Forward: list open earnings-beat markets each day with YES ask < 50c and the ask depth; paper log, sequential test per real fill (PROMOTION RULE).
