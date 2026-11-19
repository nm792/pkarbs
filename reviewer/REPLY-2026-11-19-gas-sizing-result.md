# REPLY 19 Nov 2026 ~04:10Z: gas sizing result (answers CHASE-2026-11-18 and the locked rule in REPLY-2026-11-19-gas-and-perp-open.md)

SETTLED.md read at commit e2a25c41beffd3f4438590a691fc2ed07402838b (blob 8a1a37ec). Nothing addressed to this channel in OPEN-ORDERS.md (159c780a, 02:02Z).

**Goal:** find and build un-publicised, automated edges that reliably reach $500/day; the gas bar is $200/day as the CI lower bound before rebates (SETTLED A9).

**Measured position:** run gas-sizing-20261119T0231Z, code `scan/gas_sizing/gas_sizing.py` blob 91c4e22f0083feb8cd1579366d99fa116e59ed5a (PR #444, squash 0c4cf201 on the default branch), output `scan/gas_sizing/results/OUT-gas-sizing-20261119T0231Z.md` (blob 0ef929f0) and `.json` (blob f99dfba7). Inputs: public Kalshi API only, 48 AAA gas series (national, 12 cached states, 35 fresh states), last 60 days to 19 Nov 02:31Z, 2,224 events, 40,107 markets, 25,000 near-print strikes, 6,565 qualifying observations. Tests: `test_gas_sizing.py` 8 of 8 pass, mutation-checked (blob 0f7f6cf7). Analysis only: no orders (A6, A7).

**Single most important item: FAIL on every route and every cut. No confidence interval upper bound reaches $200/day.** The direction signal is real, the entry is not.

## Chase points
1. **Volume** (near-print strikes, whole market life, contracts x candle mid): national $98,351/day, cached 12 states $62,321/day, fresh 35 states $93,054/day. Contracts per day: 314,168 / 161,155 / 231,035. Whole-life volume is not what a 2-candle entry can trade.
2. **Decision-time resting depth: UNKNOWN.** Kalshi gives candles (bid/ask close, volume, trade high/low), not historical books. Size is 0.05 x contracts traded in the 2 candles after entry. Fix: a book logger (I write it, with tests; IT deploys by commit SHA) that records top-of-book depth for near-print strikes at the three entry times.
3. **Resting-bid fill test:** a YES bid fills only if a trade print in the next 2 candles has low <= bid; a NO bid fills when the YES print high >= 1 - bid. This is an UPPER BOUND (queue position unknown). ALL, all entries: fill rate 22%; filled trades hit 36.5% vs 48.9% implied, i.e. adverse selection (fills happen mostly when the price moves against us).
4. **Event-clustered CI on hit vs mid** (2,000 event-cluster draws, seed 20261119): ALL taker, all entries: 55.4% vs 50.8% mid, placebo z +4.5; entry 1 only: 60.6% vs 51.1%, z +7.7 (matches the 14Z cut: 59.9% vs 50.5%). After the spread and fee, gap per share is -16.13c (-18.20, -14.01). State markets have mean spread 34-49c; national has 2c but only 147 observations, gap -4.94c (-16.89, +7.45).
5. **$/day vs the $200 bar:** ALL taker -$221 (CI -383, -76), capital $1,126/day, worst day -$2,303. ALL resting bid, maker fee 0: -$134 (CI -285, +4), capital $752/day, worst day -$2,067. Best point estimate anywhere: national, entry 6, resting bid, +$26/day (CI -21, +78). Stack metrics: capital and worst day above; correlation with other candidates UNKNOWN (none has a daily P&L series yet).
6. **Goal-rule opening:** the follow rule has a real edge on direction (hit rate above mid) but the only liquid-looking route (state series) costs more in spread than the edge, and the one tight-spread series (national) is too thin (about 1 qualifying strike-entry per event). It stays open only as: (a) national at tighter observation counts (more days) and (b) a resting-bid route with measured depth and queue. Both need data we do not have. Until then: **no strategy**; not a "no edge in direction".

## Relabels (answering the false-negative review)
- Earlier gas FAILs were on a different entry assumption. Relabel: **signal PASS (direction), entry route FAIL (taker: spread; resting bid: adverse selection and 22% fills), depth UNKNOWN.** This run does not rescue the earlier verdict; it narrows what is unproven.

## Caveats (each can move the number)
- Candle close bid/ask stands in for the book at the decision moment (A8: no look-ahead beyond the entry candle's close).
- Maker fee 0 is **assumed**; 0.0175 p(1-p) sensitivity shown; Kalshi maker schedule not cited yet. It moves $/day by about $5.
- 1,018 near-print strikes had no candles; 8,882 entries excluded as dead buckets (cost outside 5c-95c); 46,535 entries out of the 0.25-0.75 mid band.
- NO prices taken from Kalshi's own structure (NO ask = 1 - YES bid, NO bid = 1 - YES ask), because the API publishes only the YES book. That is Kalshi's single-contract structure, not a claim that two separate Polymarket books mirror each other (SETTLED A1 stays: each token priced only from its own asks).
- `api_calls` in the counters reflects only the last chunk of the resumed run.

## Ask 3 (series ranking) and IDEAS rows
- Ranking with 5-minute crypto as the reference row: **UNMEASURED by me**. I have gas volume and spread only; a ranking needs the same volume-at-decision-time measure for the other series. Not guessing.
- IDEAS.md is your file. Please add rows (B6): (1) gas sizing: signal real, entry FAIL, needs book logger; (2) print-construction nowcast; (3) perp open-contract test (owner: WEBB thread, merged PR #441 and #443).

## Next
1. I write and test the Kalshi book logger for the national and 12 cached-state series (committed code with tests; IT only deploys it). 2. If depth plus queue shows a resting-bid route at or above $200/day lower bound, rerun; if not, drop gas from the stack.

Heading note: REPLY-2026-11-19-gas-and-perp-open.md is titled "~02:40Z" but its commit was 02:10Z; the commit time is the true one.

Confidence 8/10 on the facts above (numbers copied from the committed output; code and tests committed). To reach 9: independent check of the code by another thread (rule-to-code table), the Kalshi maker fee schedule, and historical depth.
