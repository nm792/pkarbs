# REPLY to CHASE-2026-11-19-gas-and-perp-open-HARD (PK arbs, 19 Nov 2026 ~03:00Z)

**Goal:** find and build automated strategies that reliably make $200/day before rebates and can be stacked, with no catastrophic loss (SETTLED A9).
**Where it stands:** the perp-vs-open-contract test now has a locked rule, committed code with can-fail tests, a run and a result: `weekend-perps/RESULT-open-contracts-2026-11-19.md`, rule `weekend-perps/LOCKED-RULE-open-contracts-2026-11-19.md` (locked in 5efcc5eb before any model number), inputs and outputs in `weekend-perps/open-contracts-2026-11-19/run-2026-11-19/`. Verdict: **fails on size, edge unknown (N too small)**. Gas sizing: no result from this thread yet (see item 1).
**The one item that matters most:** the perp-vs-open test. The perp predicts the cash open (correlation 0.955, 88% sign agreement), but the contract price already holds nearly the same information (Brier 0.0351 model vs 0.0380 market at T-30, test half), and all SPX plus SPY volume in the hour before the open averages $1,394 a day, so $200 a day needs 14% of all of it at a 100% return.

## Item 1: gas sizing (CHASE-2026-11-18-gas-sizing-overdue.md)
**Exact blocker:** this thread was not given the gas item (the coordinator's relay at 02:08Z assigned only the perp test), and the Kalshi cache in `scan/` that the six points need is not in any branch I can read: `scan/` does not exist on the default branch or on `reviewer`. Owner: the coordinator assigns it, and whoever holds `scan/` commits the cache (or states where it is). I start the sizing within 15 minutes of that and commit by 06:00Z if the data is readable. Nothing has been computed, so no gas number is claimed.

## Item 2: perp open-contract locked rule and result (REVIEW-2026-11-18-perp-open-contracts.md), done early
Against the six required points:
1. Universe: every resolved SPX and SPY open event 3 Aug to 18 Nov 2026 (154 events, 77 days, none dropped). No Nasdaq or single-stock open markets exist on Polymarket (searches for "Nasdaq", "NVDA", "Dow", "Tesla" found only SPX and SPY).
2. Checkpoints T-60, T-30 (primary), T-10 min; perp-implied P(open > prior close) = Phi(x / s), with s from the training half only. The contract resolves against the prior close, not a strike.
3. Own-token pricing: no historical order books exist, so the BOOK level has n = 0 (excluded and counted, never mirrored). The FILL-PROXY level (taker-buy fills in the same token, labelled proxy) gives n = 2 at T-30 on the test half. Fee 0.04 x p x (1-p), docs.polymarket.com/trading/fees.
4. Metrics are in the result file: hit rate vs ask, edge, depth, $/day at a 10% slice with CI, event-clustered bootstrap, sign-flip placebo, train/test split by date.
5. Planted check: `test_oclib.py` (asks 5c under the model give about +4c after fee; asks at the model give about minus the fee; sign flip loses; missing asks are excluded and counted; daylight saving; fee table). All pass.
6. Verdict against $200/day: fails on size. Correlation with other candidates: not computable (no common daily series in the repo), stated as unknown. Capital: under $2 a day at a 10% slice.

Next measurement: the forward book recorder (`book_recorder.py`, tests pass, deploy task `agent/TASK-oc-book-recorder-2026-11-19.md`, due 06:00Z so the 14:30Z open is captured). Read-out on 20 Nov and weekly.

## Plausibility check (Nick rule 3, within 15 minutes of the run)
154 of 154 rows have a perp point (231 of 231 checkpoints). Polymarket vs Yahoo agreement is 153 of 154 (the miss is the SPY ex-dividend day). Perp-vs-open correlation on training rows is 0.955 (a broken join would show about 0). Own-token fills are present for 29 to 35 of 154 events per checkpoint, consistent with a median of $144 traded in the last hour per event. Plausible.

## Process (Nick 19 Nov standing rules)
All code was written and tested here. The agent only deploys committed code by SHA and runs stated commands. I read `reviewer/OPEN-ORDERS.md` at the start of this task (no order addressed to PK arbs) and will re-read the reviewer branch at least every 15 minutes while active.
