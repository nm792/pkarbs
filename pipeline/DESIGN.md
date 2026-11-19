# Systematic signal pipeline for Polymarket (design note, 19 Nov 2026)

Goal: find and build un-publicised, automated Polymarket edges worth $500/day, by industrial search
across all series instead of one idea at a time.

## What earlier searches did (so this does not repeat them)
- MECE scanner (`scanner/`): locked-payout structures (negRisk sets, covers, time ladders). Structure arbitrage only.
- Sports MECE (`notes/sports-mece-plan.md`, `shadow/`): in-play negRisk sums. One structure, one sport family.
- Forecast edges (`forecast-edges/`, 10 Nov): hand-built models per market type (tweet counts, Netflix, box office,
  temperature) plus a model-free calibration scan (`pull_scan.py`: 1,360 events, 33 cells, none passed).
  Lessons kept as rules: first causal print fill, matched placebo, event-clustered stats, count every cell tried,
  profit concentration, held-out half (memory `backtest-method-checklist`).
- Feed-lead tests (Goalserve, PandaScore, TheSports): one feed against one venue price each.
Gap: none of these ranked all series on the same footing, and none counted how many hypotheses were tried.

## The five stages and what exists
| # | Stage | Status |
|---|---|---|
| 1 | Point-in-time ingestion | `pit_store.py`: gamma `/events/keyset` (cursor param is `after_cursor`, limit>50 needs gzip) and data-api `/v2/trades`. Every stored event has `_fetched_at`. Trades are kept per token; each token is priced only from its own prints, never 1 minus the other side. Recorded books (`books.jsonl.gz`), Goalserve, PandaScore and perps join here as extra tables keyed by (token, ts) in stage 1b. |
| 2 | Candidate signals | `signals.py`: own-token features at decision time t from prints strictly before t (price, momentum over H and 4H, log volume ratio, taker imbalance, range, trade count). Library is a plain dict of functions so adding one is one line. Feed-lead and cross-market signals are stage 2b. |
| 3 | Evaluation | `evalx.py`: rank IC per day (or week when thin) against edge = win - causal fill price, ICIR/t-stat, decay by horizon (2m, 10m, 1h, 6h, 24h before end), chronological walk-forward (sign chosen on first 60% of events, scored on last 40%), Benjamini-Hochberg over every cell tried. |
| 4 | Combination and sizing | Not built. Plan: ridge/GBM on surviving signals with the same walk-forward, sized by Kelly fraction on edge net of fee and spread from the recorded books, capped per event and per family. Needs fills from real books, not prints. |
| 5 | Monitoring | Not built. Plan: nightly rerun of stage 3 on new days; alarm when live IC falls below half the backtest IC or when family volume drops. |

## Why edge = win - fill, not ROI
Rank IC against payoff ratio (win/p - 1) is mechanically non-zero even when prices are perfectly calibrated,
because a low price means a bigger win payoff. The e2e test caught this on a synthetic calibrated market.
`edge = win - p` has expectation zero for any p under calibration, so IC and its sign mean "mispricing".

## First-stage screen (Nick, 19 Nov 03:37Z)
A family is a gamma series (`series.slug`), else a title template. Ranked on
1. frequency: events per day and share of days with a resolving event (pass: >= 1/day and active on >= 50% of days);
2. volume: median event volume (pass: >= $20k);
3. late moves: where the winning token still traded before resolution. Descriptive and uses hindsight:
   T* = last print of the winner below 0.95 on its own token; report the winner's price 10 min and 1 h before T*.
   This only says "the market had not finished moving"; it is not a tradeable claim. The tradeable test is
   the ex-ante IC and calibration edge in stage 3 (decision at end time minus H, no hindsight).

## What qlib gives us and what it does not
Reuse: the ideas of Rank IC / ICIR as the standard metric, rolling train/test segments, and a recorder-style
output of every run's parameters. Not reused as code: qlib's data layer assumes a shared daily calendar of
continuously priced instruments and cross-sectional factor panels (Alpha158); Polymarket contracts are
finite-life binary claims with a known terminal payoff, irregular prints and event clustering. We did not run
qlib in this stage; adopting it later would mean writing a data handler that maps (token, decision time) to its
features and label.

## Known limits of stage 1 (stated, not hidden)
- Fills are first BUY print after decision time, a stand-in for the ask; spread and depth are not modelled.
- Trades are sampled per family (default 100 events, top 2 markets each), not the full history.
- 30-day window of closed events only; resolution anchored on gamma `endDate`; markets whose result was known
  before that are dropped when `closedTime` precedes the decision time.
- Taker fees by category are not yet netted; so nothing here is a profit claim.
- Crypto 5-minute and 15-minute series are listed but are the MFW project's; kept in the table for completeness.
