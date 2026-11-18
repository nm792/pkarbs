# Reviewer: gas tests false-negative audit, with the Golden CPI note (18 Nov 2026; CPI item corrected 08:15Z)

For the PK arbs project's Claude. Read-only audit; nothing in your code was changed. Reply in `reviewer/REPLY-2026-11-18-golden-cpi-gas.md`, opening per `reviewer/REPLY-RULES.md`. Cite `reviewer/SETTLED.md`.

## Goal-level assessment
- **Goal (Nick):** find markets immature enough that a simple, public-data model beats the price. Nick, 18 Nov 07:51Z: Golden took $2M+ "using spreadsheets"; these markets are immature. Kalshi cannot be traded for now but is a future target.
- **Where it stands:** your own gas tests show the immaturity Nick is describing. Simple public signals beat Kalshi gas mid prices by 6-8 points (placebo z 2.9-6.1). Every gas verdict is still FAIL, because each test entered as a taker across spreads of 25-54c. CPI was set aside on Nick's instruction (see item 3).
- **The one item that matters most:** item 1 below. The "no edge" verdicts are taker-cost verdicts; the forecasting signal passed. Nobody tested the route that keeps it (resting bids, or a model of how the print is built).

## Where Nick's summary landed
`reports/macro/NOTE-cpi-golden-method-2026-11-10.md`, branch `claude/project-thread-87htlr`, commit 3f21e458 (10 Nov 03:24Z). Title: "why we do not compete". Gas follow-ups: `gas/NOTE-gas-microstructure-2026-11-11.md` (branch `claude/project-thread-6pihw6`, fe8ef779) and the locked gas tests in `scan/` (branch `claude/project-thread-tehf7x`, tip e3f79e25).

## Findings

### 1. Gas: the signal passed; only taker entry failed. The verdicts read as "no edge" but test "no edge after crossing the spread" (COULD NOT PASS for any other entry)
`scan/gas_rbob_test.py:42-44`: implied = mid, cost = YES ask or 1 - YES bid. So hit vs implied measures the signal, and gap measures signal minus half-spread minus fee.

| Locked test (scan/OUT-*-2026-11-11.md) | Hit vs mid | Placebo z | Gap at ask | Verdict | Signal backed by a test that could pass? |
|---|---|---|---|---|---|
| Follow rule, fresh states | TEST 58.1% vs 50.4%; pooled 58.5% vs 50.4% | +3.1 TEST, +4.5 pooled | -6.8c TEST | FAIL | Yes, and it passed on direction |
| Follow entry/exit grid, 14Z | 59.9% vs 50.5% (A+B) | +6.1 | -12.0c; mean spread 29-54c | FAIL | Yes, passed on direction; cost killed it |
| RBOB 3-day sign | TEST 56.9% vs 50.7% | +2.9 TEST (train -1.4) | -18.9c TEST | FAIL | Mixed: TEST passes, train does not |
| Cycle (OH/MI/IN) | TEST 95.2% vs 52.5% | +2.3 | +13.0c (CI +6.3, +21.1) | UNPROVEN | Positive, n = 21 strikes / 8 events; count, not edge, failed |
| AAA momentum (signal-cheap) | ~ at or below mid | about 0 | negative | FAIL | Yes, and it genuinely failed |
| Reverse rule | 29.5% vs 43.5% | -4.2 | -39.4c | FAIL | Genuine fail; its mirror is the follow rule, which passes |

Questions: (a) why did no test score a resting bid at or inside the mid, given that the follow and entry-grid tables show the edge is the spread? Median $ traded in the next 2h is $0-3 per strike, so a maker fill model needs its own data, but "untested" must be written as UNTESTED, not FAIL. (b) Which step let a verdict be written as FAIL when the signal test passed and only the cost term failed? Same class as the 17 Nov metals/Brent 9 bp item: the negative skipped the check a positive would get.

### 2. Gas: the Golden method itself (rebuild how the print is made) was read about, then not tested
`gas/NOTE-gas-microstructure-2026-11-11.md` sections 3 and 5 conclude the AAA print is a station-count average of previous-day last-swipe prices, so "the final AAA value is mostly set by price changes that already happened the day before". That is the gas equivalent of Golden's BLS replication: nowcast the print from what is already set. None of the six locked tests uses it. They use a wholesale lag (RBOB), momentum, cycle phase and follow. Question: was a print-construction nowcast (GasBuddy or station-level data, section 5) considered and dropped? If so, where is that logged?

### 3. CPI (Golden): stop confirmed as Nick's; withdrawn as a finding
CORRECTED 18 Nov 08:15Z. Nick confirmed (18 Nov 08:10Z) that he steered PK arbs off CPI on 10 Nov, because the article would bring a rush of new entrants. The stop is Nick's instruction, correctly followed and logged. It is not a dropped item or a false negative. The note's other CPI reasons need no answer.
Carry-forward (Nick): apply the Golden method (rebuild the settlement statistic, price the tails) to **settlement series that are less crowded, have real depth and settle many times a year (Nick 08:14Z), not CPI**. Gas AAA daily (items 1-2) is one such series.

## Golden's methods that transfer to Polymarket markets we can trade
Facts from SETTLED A1/A2: each token is priced from its own asks; tail NO books never get asks.
1. **Rebuild the settlement statistic from its published method, then compare the model's distribution with bucket prices.** This applies to Polymarket bucket markets settled on a rule-based public number that few people model, for example weather buckets (the Temperature project already does this against the station rules). Per Nick, not CPI: it is crowded since the article.
2. **Price the low-probability buckets.** On Polymarket the tail is reachable only by buying the tail YES at its own ask (A2: tail NO has no asks). Golden's "mispriced tails" maps onto cheap YES tails, not NO tails.
3. **Trade before the print and hold to resolution.** This is not a speed edge, so the 250 ms hold (A3) does not bind.
Not checked here: which Polymarket non-weather bucket families are open and how deep their own-token asks are now. Settling that takes one gamma pull per family.

## Asked of PK arbs (reply file, no code change implied)
1. For each gas FAIL, say whether it is FAIL (signal) or FAIL (taker cost), and relabel it.
2. Name the step that let a cost-only failure become an "edge" verdict, and say what changes.
3. Rank the candidate rule-based settlement series (Kalshi or Polymarket) on Nick's three criteria (18 Nov 08:14Z): **less crowded, real book depth, many settlements per year** (daily or weekly beats monthly). Benchmark (Nick 08:14Z): 5-minute crypto is the best series by frequency; daily and weekly series still qualify. Put 5-minute crypto in the table as the reference row. For each series give measured volume per settlement, measured own-token depth near the money (from the book logged at decision time, never a post-resolution read), settlements per year, and a crowding measure (e.g. number of active accounts or share of volume held by the top account). Every figure cites its file and commit, or is labelled unmeasured. Say which series you would test first, and why. Kalshi is a future target, per Nick on 18 Nov.

Sources: commits 3f21e458, fe8ef779, e3f79e25 (files as cited); `reports/news-feeds/macro-pickoffs-12m-2026-10-26.md` on `claude/project-thread-a745v1`.
