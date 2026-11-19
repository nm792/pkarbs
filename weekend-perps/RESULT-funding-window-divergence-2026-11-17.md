# Result: divergence of the perp from its oracle/index inside funding windows (rule: LOCKED-RULE-funding-window-divergence-2026-11-17.md, merged in PR #371 before any number)

Scope per Nick (17 Nov 01:06Z): convergence at the reset is the mechanism, not a finding. This reports only how far the perp gets from the oracle between settlements and whether it can be traded before the reset. The earlier weekend "open lands on the perp" and overshoot results are withdrawn as findings; they measured the reset.
Venues: Hyperliquid funds hourly (xyz funding is scaled 0.5, so the hourly rate is about premium x 0.0625; flx has multiplier 0.0, i.e. no funding anchor); Polymarket perps fund hourly. Premium = (impact mid / oracle) - 1 averaged over the hour. History is hourly only; the intra-hour path is from a 30-minute live sample.

## 1. Size and persistence, hourly history (108 perps with >= 60 days, OI terciles $1.8M / $11.5M; xyz, flx, km)
| Tier, session | Hours | median / p90 / p99 abs premium (bp) | % of hours >= 25 bp | % >= 50 bp | next hour not reverted | AR(1) |
|---|---|---|---|---|---|---|
| thin, weekend | 42k | 9 / 36 / 98 | 17% | 5.7% | 79% | 0.78 |
| thin, weekday US hours | 35k | 6 / 26 / 99 | 11% | 4.0% | 66% | 0.63 |
| thin, weekday other | 69k | 9 / 39 / 119 | 19% | 6.6% | 65% | 0.64 |
| mid, weekend | 52k | 6 / 24 / 66 | 9% | 2.2% | 67% | 0.60 |
| mid, weekday US | 43k | 5 / 12 / 52 | 3% | 1.1% | 67% | 0.67 |
| mid, weekday other | 85k | 5 / 16 / 60 | 5% | 1.5% | 65% | 0.66 |
| liquid, weekend | 66k | 4 / 18 / 63 | 6% | 1.6% | 55% | 0.51 |
| liquid, weekday US | 55k | 4 / 14 / 96 | 6% | 3.0% | 62% | 0.64 |
| liquid, weekday other | 109k | 4 / 15 / 77 | 6% | 2.2% | 63% | 0.71 |
"Not reverted" = among hours with premium >= 25 bp, the next settlement hour has the same sign and at least half the size. Thin perps run a >= 25 bp gap in 17-19% of hours and 65-79% of those are still open an hour later (median run 1-2 h). Liquid perps are within about 4 bp half the time. Funding is the only restoring force and it is weak: mean abs funding is 0.4-0.9 bp per hour, about 3-4 bp per hour when the premium is 50+ bp.

## 2. Tradable reversion test (locked trade: fade a premium >= 50 bp at the hour close, exit one hour later, 2 x (9 bp fee + stressed half-spread), funding received included; weekly-cluster 95% CI)
| Tier, session | Events | Gross | Funding received | Net | 95% CI |
|---|---|---|---|---|---|
| thin weekend | 1,917 | +3.3 | +3.7 | -88 | -95 to -82 |
| thin weekday US | 1,142 | +6.9 | +3.1 | -73 | -85 to -63 |
| thin weekday other | 3,955 | +7.7 | +3.3 | -88 | -97 to -80 |
| mid weekend | 818 | +7.5 | +2.4 | -41 | -54 to -30 |
| mid weekday US | 425 | -11.9 | +3.4 | -70 | -86 to -55 |
| mid weekday other | 1,147 | +11.4 | +2.9 | -42 | -53 to -32 |
| liquid weekend | 443 | +15.0 | +1.2 | -7 | -25 to +10 |
| liquid weekday US | 1,087 | +2.9 | +3.4 | -17 | -27 to -8 |
| liquid weekday other | 1,807 | +1.6 | +4.0 | -19 | -27 to -11 |
Locked rule outcome: NO TRADABLE REVERSION in any cell. The gap persists (section 1) but the perp price itself barely moves back within an hour (gross +3 to +15 bp), funding pays 1-4 bp, and fees alone are 18 bp round trip. Spread stress is large for the thin tier (live half-spreads of tens of bp). Not tested because not locked: holding the faded side for many settlements to collect funding (at 3-4 bp per hour it would need 5+ hours of an unchanged gap, and thin gaps persist 1-2 hours median).

## 3. Intra-hour, live 5 s sample, 30 min, 01:03-01:33Z Tue (US after hours, metals/oil futures open)
- Liquid Hyperliquid/Polymarket commodity and index perps (gold, silver, CL, Brent, SP500, XYZ100, EUR, platinum, palladium, copper): median mark-oracle gap 1-8 bp, max 3-23 bp, never >= 25 bp.
- Polymarket after-hours equities: NVDA gap >= 25 bp 11% of the time (longest 150 s), AMD 5% (90 s), MU 3% (40 s), TSLA 1% (20 s). They revert within about 2.5 minutes, which is far inside a settlement window.
- xyz thin: URNM >= 25 bp 33% of the time (longest 580 s); BIRD a constant 130-160 bp gap for the whole 30 minutes (oracle updated 60 times, mark never closed the gap).
- flx COPPER/GAS/OIL/SILVER and km BMNR/RTX: the oracle did not change once in 30 minutes (0 changes) with the mark parked 12-430 bp from it (flx silver 130 bp, km BMNR 326 bp, km RTX 431 bp); flx has no funding. These perps are not tracking the underlying at this hour at all.
Limits: one 30-minute session, one time of day; hourly history cannot show intra-hour excursions or when in the hour a gap opened; candle closes are trade prices; costs use live half-spreads from the time of analysis, stressed 3x; HIP-3 fee rate assumed 9 bp per side (HL 4.5 bp base, doubled); the trade.xyz weekend oracle/discovery-bound docs could not be fetched from this container (hosts blocked), so the mechanics come from search summaries of those docs (mark bounded by discovery bounds around the last external price, oracle reset to the external price at the reopen) and from the API.
Next if wanted: log mark/oracle at 5 s through the Sunday 23 Nov reopen on the loggers, and a locked "carry" rule.
