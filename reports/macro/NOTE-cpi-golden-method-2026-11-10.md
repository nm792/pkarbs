# What the Kalshi CPI trader (Brian Golden) tells us, and why we do not compete (10 Nov 2026)

Desk check, no orders, no server. Nick's call (10 Nov 03:23Z): do not compete with him; stop the CPI model build.

## What Bloomberg actually says (read directly, 10 Nov)
Bloomberg, 13 Oct 2026, Ritchie and Tsekova. Confirmed in the article text I could fetch (the opening only; the rest is paywalled):
- Golden is 44, a former theater director, trades from a garage in Los Angeles, says he is "not a math guy".
- "Over $2 million in profits across Kalshi contracts tied to economic questions, more than three times as much as the next-highest-earning public account in the category", per Kalshi dashboards and data reviewed by Bloomberg.
- The bulk of it is consumer prices (CPI).
Not verified: "beat bank economists on 15 of 20 reports" and "custom spreadsheet models from BLS data". Those sit past the paywall; only secondary posts repeat them.

## What the method tells us
1. It is a public-data, simple-model edge, not a speed edge. He trades the print before it comes out, not the second after.
2. It lives where few people model: CPI is one of the most watched numbers, but the Kalshi contracts on it were thin. Next-highest public account in the category earns under a third of his total.
3. It needs one thing we do not have: a model that is right more often than the market price, shown out of sample. I did not get to build or test one. Unknown, settled by a backtest of model vs Kalshi and Polymarket pre-release prices over about 20 releases.

## Why we should not chase it
- The Bloomberg profile advertises the niche. Copycats are likely, and our own measured history of release-time trading shows bots arrived over 2026 (first winning prints +11 s Oct-Apr, +4-6 s May-Oct; macro-pickoffs-12m-2026-10-26.md).
- Size is small. Polymarket US CPI events (headline MoM+YoY and core MoM+YoY), lifetime volume per release, measured from gamma: Jul 2026 $1.27M, Aug $0.33M, Sep $0.53M, Oct $0.23M so far (market open until the release). Kalshi closes its CPI markets 1-5 minutes before the release (26 Oct check, 14 events), so they are pre-release-only books.
- We hold to resolution, but a forecasting edge needs a repeated, judged-once test, and the profile starts the clock on crowding.

## What I think happens to that market (estimate, not measured)
Spreads tighten and the easy mispricings shrink as more people copy a spreadsheet CPI model. Whether it already has: unknown. What would settle it: compare pre-release price error (market-implied vs print) for Aug-Oct against Nov-Dec 2026 and later, plus Kalshi/Polymarket CPI volume per release. Today's 8:30 ET release is the first one since the profile.

Confidence 7/10 that this is the right call for us. 9 would need the 20-release backtest, or Bloomberg's full text for the 15-of-20 claim.
