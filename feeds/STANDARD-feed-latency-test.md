# STANDARD: feed latency test (canonical, owned by Nick)

Version 1, 12 Nov 2026. Every feed trial, feed test or "is feed X faster" question in this project CITES this file by name and version. It does not restate the numbers. If a task needs a different number, it says "deviation from STANDARD v1: <what, why>" and Nick approves it before data is collected. Only Nick changes this file.

## 1. The benchmark is always the price
- The benchmark is the Polymarket price (or the target venue's price, named in the task). Never another feed.
- "Beat TheSports", "beat ESPN", "beat HLTV" is NEVER a pass condition. On CS2 the price moves 10-60 s before TheSports, so beating it proves nothing.
- Other feeds are side comparisons only. Report them, label them "information only", never gate on them.

## 2. Definitions
- Event: a state change diffed from consecutive feed messages (score, round, kill, point, ball). The task names the event types before data.
- Match to the market by team names plus start time. Side by settlement, never by price co-movement.
- Receive time: ONE shared clock. The feed message and the price rows are stamped by the same host (chrony-synced, ns) in the same process or the same capture set. HTTP Date headers and vendor timestamps are logged but never used for lead. State the resolution (poll interval/2, book poll latency; /books rows are late by about 0.1-2 s).
- Price-move onset: first mid move of at least 2c in the event direction inside [-60 s, +60 s] around our receive time.
- Lead = onset time minus our receive time. Positive = the feed was first.
- Placebo: 10 random event-free times in the same match, same windows, same procedure. Every lead is shown next to its placebo with n.

## 3. The bar (per sport or game title, separately)
Pass only if ALL hold:
1. n >= 30 events (and >= 30 events per volume stratum if strata are reported).
2. Median (real minus placebo) lead >= +2.0 s.
3. Bootstrap 95% CI, resampled by match, excludes 0.
4. The price moves AFTER the feed message in >= 60% of events.
Else: "no lead", drop that sport/title. Fewer than 30 events = "unknown, settled by <what, when>", never a pass or fail.

## 4. Pre-registration and audit
- The rule (events, window, thresholds, strata, sample size, deadline) is written and committed BEFORE any data is read. Locked after that. One evaluation at the stated N, no peeking, no re-picking on the same data.
- An independent audit (a thread that did not run the test) must check: z on real P&L spread, same-event random placebo, top-3 concentration, cluster-robust t, variant-count correction, log score vs market first print. No pass or fail counts, and none is relayed, before the audit.
- Report numbers labelled: "sim on real data", "synthetic", or "estimate". Never call an estimate measured.

## 5. Money bar (only if section 3 passes)
- Pre-registered paper rule filled only from observed book depth, with the 1 s sports delay modelled and the price after our entry, not the first print.
- Average net P&L >= 3x the feed's daily fee per title (fee/30), and bootstrap 95% lower bound >= 1x the daily fee. (PandaScore: EUR 400/day per title, lower bound EUR 133/day.)
- Never quote first-print-sized backtest P&L as capacity. Quote the capacity result.

## 6. Existing tests: status against this standard (12 Nov 2026)
| Test | Standard v1 status |
|---|---|
| Goalserve trial (#274/#276 task + odds addendum) | Aligned after amendment (comparator gate removed; no data collected yet). |
| PandaScore (#278/#279) | Aligned (+2 s, PM benchmark). Note feeds/NOTE-pandascore-trial-plan section 4 (+5 s, >=40 games/>=200 events) is superseded. |
| CS2 lead3 (#280) | Compatible: tests whether the price leads the feed, benchmark is the price. Different pass rule (map-clustered, pre/post split) because it is an audit of a lead claim, not a feed trial. |
| TheSports T1 / D1 (#213, #277) | NOT a latency test: trading-rule tests, 90% CI, n=60/40. Running on data, unchanged. T1 closed FAIL. Flag only. |
| LSports / GRID gate | Arrival relative to PM onset (benchmark is the price). Different bar (<= 2 s tennis, <= 5 s LoL after onset). Not yet running. Flag. |
