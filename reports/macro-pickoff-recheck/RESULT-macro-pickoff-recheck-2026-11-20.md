# Macro-release stale-quote pickoff, rechecked as a stack layer (20 Nov 2026)

Project goal: $500/day automated on Polymarket, built from stacked edges (Nick, 20 Nov 06:31Z "stack layers").
Where this stands: a small positive layer, **about $12-40/day stand-alone, central $20/day, for a sub-second bot; NOT proven; hidden-depth upside untested**. Stack layer: **YES, if automated and size-capped**.
Origin: reports/news-feeds/macro-pickoffs-12m-2026-10-26.md (f778d9b9ce, 95b59f5aa3), plan book-capture-plan-2026-10-26.md (56e6fd1541). Audit row 8 of audit/STACK-LAYER-AUDIT-2026-11-20.md (6b8746b005).
Code and outputs: this folder. Inputs: Polymarket gamma + Data API v2 (`/v2/trades?event_id=`), pulled 20 Nov 2026 ~06:50Z. Run: fetch.py -> add_unresolved.py -> trades.py -> analyse.py (analyse.out, days.json) -> summarize.py (summarize.out).

## 1. Result, stand-alone $/day (all from summarize.out)

Whole-market pool (positive taker edge in the first 30 s after the release, valued at the settled outcome) for CPI, jobs, FOMC, PPI: **38 release days, 20 Oct 2025 to 13 Nov 2026, gross $85,881, net of 0.05 fee $82,450, net of 0.01 fee $85,195.** Reproduces the 26 Oct scan ($82,039 gross over 34 days) plus the 4 new days ($3,669): FOMC 28 Oct $1,404, jobs 6 Nov $240, CPI 10 Nov $1,441, PPI 13 Nov $584. Core PCE added as a fifth family: 4 days, $2,205 (not in the totals below).

| Case (net of 0.01 fee) | Whole-market $/calendar day | Our share | Ours $/day |
|---|---|---|---|
| All 38 days | $218 | 30% | $65 |
| Excluding the 29 Jul FOMC day ($33.9k, 40% of the year) | $132 | 30% | $40 (same kill test as before: was $38) |
| Bot era (May-Nov 2026) excluding 29 Jul | $173 | 10-25% of the part reachable at >6 s (68%) | **$12-29** |
| Bot era incl. 29 Jul, bootstrap over 23 release days (45 days/yr) | | 10% / 20% / 30% | 5th / 50th / 95th pct: $17 / $35 / $60; $35 / $70 / $116; $53 / $104 / $174 (heavy tail from the Jul FOMC day; summarize.out) |

Old estimate for a 1-3 s bot was $8-21; the rerun gives $12-29 because Oct 14 CPI ($8.9k) and the newest days pushed the bot-era base up. **Central $20/day, range $12-40.** It is lumpy: 9 days at least 3x the median carry $65.5k of $88.1k (74%, analyse.out, all 47 listed days incl. PCE); one FOMC day (29 Jul, 33.9k) is 40%. Expect 2-4 paying days a month, most months near $0-500 in pool.

## 2. Fees (cited)

- Today every one of these markets is `feeType economics_fees`, `feeSchedule.rate 0.05`, takerOnly (gamma, events 1376034 CPI, 770450 FOMC, 1357781 jobs, 1278384 PCE, read 20 Nov).
- Docs (https://docs.polymarket.com/programs/fee-and-rebate-changes-november-2026.md): from 20 Nov 23:59 UTC **Economics goes 0.05 to 0.01; Finance goes 0.04 to 0.05.** CPI, jobs, FOMC and PCE carry the `economics_fees` type, so they fall to **0.01, not 0.05**. Assumption to confirm: read `feeSchedule.rate` on one of these markets after 23:59Z on 20 Nov.
- Effect is small: pool net rises 3.3% ($82,450 -> $85,195), about +$7/day whole-market, +$2/day at 30% share. Edges sit at prices near 0 and 1, where p(1-p) is tiny.
- No taker delay: `secondsDelay` is empty on these markets (the 1 s delay is on CS2/Dota sports markets only).
- Taker rebate: nothing below $200k/30-day weighted volume.

## 3. Latency needed

- First winning print after the release, block time, bot era (23 days): median +6 s, range 0 to +10 s (days.json `first`). Pool by block second, bot era excluding 29 Jul: <=4 s $2.3k (7%), 5-6 s $8.6k (25%), 7-10 s $15.2k (44%), 11-30 s $8.3k (24%).
- Block time lags matching by a few seconds (estimate, unmeasured). So a pool share of about 32% is only reachable by an order that matches within about 6 s block time, i.e. read-to-submit well under 1 s with the order pre-signed per bracket. A 1-3 s bot reaches about 68% of the pool (the part after +6 s) but competes there with the repeat release bots (26 Oct scan: median 14 wallets and top wallet 53% of a day; analyse.out this run: top-3 wallets take 35% of the year pool, with 2 wallets at 14% each).
- Measured nothing on our own release-to-match time. One bounded live timing test (tiny pre-armed order on one bracket) would turn the share assumption into a number; needs Nick's go-ahead.

## 4. Can it be automated as a layer?

Yes in principle: scheduled releases (BLS/BEA/Fed calendars), a parser per release, orders mapped to brackets and pre-signed. Real risks: a wrong parse or wrong bracket at 0.8 loses 0.8 a share, so it needs a hard per-release notional cap and a two-source check (costs speed). Size is limited by what rests, not by capital: the largest steady day was $2.6k pool across all takers. Needs a funded account with order permissions (not yet used for this). Build effort not estimated here.

## 5. The hidden-depth question (the 1.31x test) is still open

- Rule: pass if reachable stale depth at R+1 s is at least 1.31x the printed pool (book-capture-plan-2026-10-26.md). FOMC 28 Oct capture was lost (sandbox froze); no jobs or CPI capture result exists on any branch I searched (a745v1, reviewer, project-thread branches): **UNVERIFIED that they ran at all; treat as no data.**
- Fresh live-book upper bound, 20 Nov, informed-taker EV with levels within 10c of the touch (live_book_bound.py): Dec CPI set $4.9k (vs printed CPI-day median $1.4k, mean $2.0k: 2.4-3.4x), Dec jobs $2.6k (vs median $485, mean $757: 3.4-5x), Oct core PCE $1.4k (PCE median $127). FOMC Dec bound $159k is not usable (97c+ bids a maker would pull). These are weeks-early upper bounds, so they cannot settle it; they match the 2-5x seen on 26 Oct.
- If the hidden depth is real the sub-second case could reach $50+/day stand-alone (earlier table: $65 middle, $120 upper). Untested.

## 6. What settles it (forward, read-only)

Forward recorder committed here (capture.py, score_capture.py, arm.py, releases.json): REST /books at 4 Hz plus websocket, R-120 s to R+60 s, scored automatically at R+10 min (provisional winners) and R+26 h (resolved) into results.tsv. Dry-run plumbing test passed 20 Nov 06:56Z in this container (112 polls, 0 errors; scorer gates passed; this was not a release, so the ratio is meaningless). Scorer now uses Data API v2 and takes the fee rate.

| Release | R (UTC) | Events |
|---|---|---|
| Core PCE Oct | 25 Nov 13:30 | 1278384, 1278380 |
| Jobs Nov | 4 Dec 13:30 | 1357781, 1357780 |
| FOMC Dec | 9 Dec 19:00 (verify on federalreserve.gov) | 770450 |
| CPI Nov | 10 Dec 13:30 | 1376034, 1375477, 1366219, 1366218 |

Four releases gives a first read on RP/P, not a go-live signal. Verdict after 10 Dec: stack layer confirmed if ΣRP >= 1.31 ΣP, else it stays a $12-29/day sub-second layer. Run on the server, not the Composio sandbox.

## 7. Data issues found

- Oct CPI YoY (1189074) and core YoY (1189689) were still not resolved on gamma 20 Nov (closed=False, no closedTime) and had 0 prints in the first 60 s after the 10 Nov release, so they add $0 whatever the winner (add_unresolved.py infers none).
- Day list contains 5 near-empty mis-matched days (foreign or partial events, notional under $100); summarize.py drops them.
- Core PCE detection used the same 12:30/13:30Z slots; only 4 PCE days, small.

Confidence 6/10. Pool numbers 8/10 (reproduce the old scan, the Data API v2 pull is complete to R-10 min). Share and $/day 5/10 (assumed 10-30%, no own fills). Hidden depth 3/10 (no capture). To reach 9: the four forward captures above, one live timing test, and the post-23:59Z feeSchedule read.
