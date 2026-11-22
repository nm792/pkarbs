# MECHANICS: PandaScore CS2 / Dota 2 feed vs Polymarket (PandaScore thread, 20 Nov 2026 ~01:00Z)

Scope: the chain every PandaScore-triggered fill must go through. Each step is DOCUMENTED (quote and URL) or MEASURED (file, commit), or marked **UNMEASURED / NOT IN DOCS**. Docs read 20 Nov ~00:50Z: https://docs.polymarket.com/concepts/order-lifecycle.md, /trading/fees.md, /programs/fee-and-rebate-changes-november-2026.md, /market-data/market-details.md, /market-data/realtime-data.md, /concepts/resolution.md, /trading/matching-engine.md, /trading/place-orders.md; PandaScore guide in repo `feeds/PandaScore-low-latency-feed-llm-guide-2026-11-13.md` and `feeds/PandaScore-low-latency-feed-counter-strike-2026-11-18.html` (vendor docs, developers.pandascore.co; docs.pandascore.co is blocked from the cloud sandbox).

**What the current test is:** the PREREG sequential test (feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md) measures TIMING: PandaScore receive time versus first mid move >=2c in each Polymarket token's own book. It is not a fill simulation. Steps 3 to 5 below are not inputs to it. They block any P&L or "tradeable" claim, and that claim is NOT MADE.

## 0. Resolution (verbatim from live markets, gamma /events 20 Nov 00:5xZ; file `cs_sample` not committed, query in this note's last section)
- CS2 match winner (Privateer Gaming vs Spirit HU): resolutionSource `https://hltv.org`. "The resolution source for this market will be official information from https://hltv.org. However, if https://hltv.org has not published final results within 2 hours after the event's conclusion, a consensus of credible reporting may be used instead including video evidence."
- CS2 Map N Winner (ALKA vs paiN Academy, child_moneyline): "If the match begins but is not completed, and Map 1 is concluded with a winner determined, this market will resolve based on the completed Map 1. If Map 1 is not completed for any reason, this market will resolve 50-50."
- Dota 2 Game 1 market (Aurora vs Astra Invicta, BLAST Slam Group D): resolutionSource `https://www.dotabuff.com`; "Game 1 ... If Game 1 is not completed for any reason, this market will resolve 50-50."
- Mechanism: DOCUMENTED, /concepts/resolution.md: UMA Optimistic Oracle, proposal, 2-hour challenge period, dispute escalates to a 24-48 h debate and DVM vote. We hold nothing to resolution (Nick, 11 Nov), so this only matters for the maps/games-vs-match mapping in the test.

## 1. Real event -> PandaScore message
- DOCUMENTED (vendor guide, section 1): feed "delivers live esports match data faster than public live streams"; broadcast streams "carry a 3-4 minute delay". **No latency number versus the venue is published.** Push over WebSocket per match, socket opens 15 minutes before scheduled start (`endpoint.opens_at`), no snapshot on connect, no heartbeat.
- DOCUMENTED (CS2 page): each message has a `latency` list of `{field, delay}`; the docs example shows delays 0 and 13234 (ms). The delay is per field, relative to the fastest field in the message (our reading of the example, NOT stated as a rule: marked ASSUMED in ASSUMPTIONS).
- MEASURED: `updated_at` lag versus our receive clock is checked at +45 s by the live probe preflight (it/REPLY-2026-11-19-live_probe_cs2.py, "plausible updated_at lag"); IT paste agent/status/pandascore.md, commit e91594ee8f: PREFLIGHT all five checks true at 10:39Z. Distribution of the lag: **not yet reported** (owed from the first probe cycle JSON).

## 2. PandaScore -> our process
- MEASURED: clock offset 0.000161 s (chrony, probe preflight 10:39Z, commit e91594ee8f). The PandaScore capture, the Polymarket book recorder and the probe all run on the same host and clock. Network latency PandaScore->host and Polymarket->host: **UNMEASURED** (we have only receive times). Every lead we report is therefore "receive-to-receive" and includes both unknown network paths.

## 3. Signal -> send -> CLOB (needed only for a trading rule)
- DOCUMENTED (order-lifecycle.md): order is signed (EIP712), submitted to the CLOB operator, which validates signature, balance, allowance and tick size.
- **UNMEASURED:** host-to-CLOB order round-trip time. No order has ever been sent by this project. Proposed measurement (no order): timed HTTPS GET to the public CLOB endpoints from the same host, 100 samples; owner IT/PandaScore thread, not yet routed.
- MEASURED (gamma + `GET https://clob.polymarket.com/clob-markets/{condition}`, CS2 ALKA vs paiN, Privateer vs Spirit): tick size `orderPriceMinTickSize` 0.01 (Map 1 Winner 0.001), `orderMinSize` 5 (shares), `acceptingOrders` true.

## 4. Taker delay (the "250 ms hold" step: does NOT apply to CS2/Dota, a 1 s delay does)
- DOCUMENTED (order-lifecycle.md): "Taker delay: used on selected crypto and finance up/down markets. The order is held for 250 ms ... To check a specific market, call GET https://clob.polymarket.com/clob-markets/{condition_id} and look for `itode: true`." And: "Sports/game delay: enabled on configured sports markets around live game conditions. The order waits for the market's configured delay window before matching. During either delay, the order is pending and cannot be canceled. If the market, balance, allowance, or risk checks fail when the delay expires, the order is rejected instead of matching."
- MEASURED: all four CS2 market types (moneyline, child_moneyline Map 1 and Map 2, totals) and the Dota 2 market show `secondsDelay: 1` in gamma; the clob-markets reply shows `"sd": 1` and no `itode`. So a CS2/Dota taker order waits **1 second** then re-validates, and cannot be cancelled in that second. Resting (maker) orders are not delayed.
- Consequence for our bar: STANDARD v1 passes at median lead >= +2.0 s. A taker needs lead > 1 s delay + send latency (UNMEASURED) + the price already having moved when the delay ends. A 2.0 s lead leaves at most ~1 s for send latency and for other bots, before any edge. **So v1 pass does not imply a tradeable lead.** Open item: pre-register a tradeability threshold only after step 3 is measured.

## 5. Queue / price-time priority and who crosses
- **NOT IN THE DOCS WE READ.** None of the pages above states the matching priority rule (price-time or other) or how a delayed taker order is placed relative to the book. ASSUMED (price-time), not used by any current run. A maker strategy (resting order that a taker later crosses) cannot be simulated until this is confirmed from venue docs or measured (own order on a quiet book).
- DOCUMENTED: "Price improvement always benefits the taker" (order-lifecycle.md): a resting order fills at its own price.

## 6. Matching engine restarts
- DOCUMENTED (/trading/matching-engine.md): order actions reject during a restart; afterwards two minutes of post-only mode. Any live window must tolerate this; none relevant to the timing test.

## 7. WebSocket broadcast
- DOCUMENTED (/market-data/realtime-data.md): market channel events `book`, `price_change`, `last_trade_price`, `tick_size_change`, `best_bid_ask`; every event has a `timestamp` string in unix milliseconds. Whose clock stamps it is not stated there; ASSUMED server-side.
- MEASURED: probe preflight checks Polymarket server-timestamp lag against our receive time (plausible, check passed 10:39Z). The onset test uses OUR receive time, not the server timestamp.

## 8. Settlement
- DOCUMENTED (order-lifecycle.md): matched trade goes to chain; statuses MATCHED, MINED, CONFIRMED (terminal), RETRYING, FAILED. Settlement is atomic. Not used in the timing test. The Reviewer's rule (on-chain block time is not match time) is respected: block time is never used.

## 9. Fees
- DOCUMENTED (/trading/fees.md, current): taker fee = C x feeRate x p x (1 - p); sports feeRate 0.05; makers never pay; maker rebate 15% for sports. MEASURED in gamma for the CS2 and Dota markets: `feeSchedule {exponent 1, rate 0.05, takerOnly true, rebateRate 0.15}`, type `sports_fees_v3`.
- DOCUMENTED (/programs/fee-and-rebate-changes-november-2026.md): from 20 Nov 23:59Z "All sports, including NFL and college football" coefficient 0.05: unchanged for CS2/Dota (esports counted as sports by gamma `feeSchedule`: MEASURED; the doc table does not list esports by name, so the coefficient after 23:59Z is re-read from gamma on 21 Nov).
- Size of the fee: at p = 0.50 a taker pays 0.05 x 0.25 = **1.25 cents per share**; the 2c onset threshold is comparable. Any "edge" figure must be net of this.

## Contradictions between our code/notes and the docs
1. The Reviewer's chain lists a 250 ms hold; CS2/Dota markets use a 1 s sports delay (secondsDelay 1). Our PREREG bar (+2.0 s) was set before this was read.
2. Past notes treated the feed lead as "the" edge; the docs imply a taker pays 1 s delay + fee 0.05 p(1-p); only a lead well above ~1 s plus measured send latency is usable.
3. Queue priority is assumed, not documented. No maker result may be reported.
4. Network paths PandaScore->host and Polymarket->host are unmeasured, so a measured lead is not an executable lead.

## Reproduce the market facts
`GET https://gamma-api.polymarket.com/events?closed=false&active=true&limit=100&offset=N&start_date_min=..&start_date_max=..` with `Accept-Encoding: gzip`; fields `secondsDelay`, `orderPriceMinTickSize`, `orderMinSize`, `resolutionSource`, `feeSchedule`, `description`. `GET https://clob.polymarket.com/clob-markets/{conditionId}` fields `sd`, `mts`, `mos`, `fd`, `itode` (absent). Sample condition ids: 0x578f9b38daa9d190c368ec321e025089477d13e31e7aa3a410c9fc84b44587e9 (Privateer Gaming vs Spirit HU).
