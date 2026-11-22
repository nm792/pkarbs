# PK arbs: status against goals (22 Nov 2026, 05:30Z / 13:30 Hong Kong time)

Reviewer, pkarbs reviewer branch. Times are UTC unless marked. Every number cites its source. Facts, not strategy views.

## 1. Goal
- Find and build automated Polymarket edges. Each one is judged alone on **reliably $200/day before rebates**, on the lower confidence bound with realistic fills (SETTLED A9, Nick 18 Nov 08:18Z). Rebates are reported separately.
- Edges are meant to stack: each is judged alone, then on correlation, shared capital and worst day (Nick 18 Nov 08:21Z).
- Paper only. Never trade or stage orders. Kalshi is a future target, analysis only.
- Method: MODELLING-PRINCIPLES.md (standing for PK since 21 Nov 06:51Z). No hindsight; shrink and rank instead of pass/fail; positive control and power before any verdict; sequential stops; capacity first.

## 2. Where each strategy stands
"% of $200" uses the best measured figure, which is often an upper bound.

| # | Strategy | Best measured $/day | % of $200 | Status | Source |
|---|---|---|---|---|---|
| 1 | **Polymarket AAA gas daily, `post`** (buy the bucket the AAA page shows, 03:15-04:00 ET) | $2.63/day backtest (35 events), with fills at recorded prints, an upper bound | 1.3% | Paper code accepted (R-007 to R-009). **Not scored yet.** At the registered sigma ($10.59/day), success needs 103 days, beyond the 60-day maximum: at day 60 the interval half-width is $4.49, above the $2.60 edge. Success is reachable only if the live edge is about 1.7x the backtest. | REPLY 15c43a29; AUDIT-2026-11-22 rows 5, 7 (R-020) |
| 2 | Gas daily, `yes_fav` and `no_out` (shadow) | v2 all rules $11.74/day; without 3 days -$14.3 | 5.9% | Post hoc; shadow cells, ranked | 15c43a29 |
| 3 | Reviewer gas prototype (follow nowcast) | +37c per $ (CI -16 to +78, 32 days); $32/day at 100% of prints, ~$3/day at a 10% slice | 1.5% | Underpowered; resting depth unmeasured | IDEAS 2b, prototypes/gas 38af8276 |
| 4 | Kalshi AAA gas daily (7 signals) | best cell national +$26/day; taker -$221; resting bid -$134 (adverse selection) | 13% | CLOSED. The signal beat the mid but not the costs; Kalshi is not tradable now | a466e37c, 08e1bbc2 |
| 5 | Golden method (rebuild the statistic, price tails) | n/a | n/a | CPI parked by Nick (10 Nov, crowding). The method is being applied through gas (rows 1-4). The AAA print nowcast from station data (IDEAS 3) is UNTESTED | IDEAS 1, 3 |
| 6 | Perp prices Polymarket "SPX opens up/down" contracts | stale share +$0.53/day (CI -5 to +6); ~$3.5k/day buy flow; reprices in ~2 min | 0.3% | FAIL on size, edge unknown | ad0099e1, 0a5c06ad |
| 7 | Weekend perps: Monday open, post-open drift, overshoot, commodity/FX reopen, divergence, metals/Brent | none tradable | 0% | Mostly NOT PASSED or no edge. Metals/Brent was costed at 9 bp vs the measured 0.9 bp: rerun outcome not seen | IDEAS 4-10 |
| 8 | Sports/esports feed leads (Goalserve, PandaScore, OddsPapi, NHL, TheSports, LSports) | none valid | 0% | **No valid result in any trial.** PandaScore CS2 kill lead +0.83c is below the 1.25c taker fee. Goalserve's look has had no Polymarket side since 20 Nov 04:11Z | REVIEW-2026-11-22-sports-esports-feeds.md (R-021 to R-024) |
| 9 | Sports MECE set arbs (both-token sums) | $46.67 at 0 ms delay, $0 at the real 1 s delay | 0% | DEAD at the measured delay | same review, row 18 |
| 10 | In-play maker (RN1 clone) / event-only post-only bids | NBA ~$70/day **simulated**; 0 live fills | 35% (sim only) | Sim only; current status unconfirmed by the project | IDEAS 17, 18 |
| 11 | Mentions word base rate (Polymarket 10c entry) | unmeasured | unknown | Statistical PASS on Polymarket, "economically tiny". Kalshi leans pass. Forward test had 0 scored events on 11 Nov; no later count | IDEAS 25 |
| 12 | Up/down rebate market making | moved to MFW (Nick 22 Nov 05:22Z) | n/a | Off PK list | Nick 05:22Z |
| 13 | Forecast edges (Netflix, MrBeast, box office, tweets), macro pickoffs, Kalshi index leader, own CS2 model | none | 0% | None passed or unconfirmed | IDEAS 12, 21, 23, 24, 27 |

**Stack today: $0/day proven.** No strategy has a positive lower bound with realistic fills. The largest figures (rows 10 and 12) are simulations or ceilings, not tests.

## 3. Proven vs not
Proven:
- The gas paper harness rejects later books, superseded books and stale books, and applies the 250 ms hold (planted tests, 20293df7; R-008, R-009). It is deployed and passes on the server (IT 11:18Z 21 Nov, 07d5a323).
- Simple public signals beat the Kalshi gas mid (placebo z 2.9-6.1), but not after costs (REVIEW-2026-11-18 item 1).
- The AAA page is readable through TinyFish (22 Nov 03:23Z baseline, monitor 5c663110).

Not proven:
- Any strategy at or near $200/day.
- Gas fills at decision-time own-token asks (not one scored day yet).
- Any sports or esports lead.
- Gas page-change time (03:15 ET is Nick's figure, not measured).

## 4. Blockers
1. **Gas hindsight defect (R-020):** both page loggers stamp the time before the request, so the fill book can come before the page value arrived. It must be fixed before 22 Nov is scored.
2. **Gas power:** success is unreachable within 60 days at the backtest edge (AUDIT row 7). The result can only be "futile" or "inconclusive, ranked" unless the live edge is larger.
3. **Order-book logger** stopped at 09:29:59Z on 21 Nov. The IT restart proof is due 06:45Z 22 Nov (trading-test IT-OPS-2026-11-22-0340Z, 80e87031).
4. **Sports:** no server read since about 21:42Z 20 Nov (R-024). Goalserve has no Polymarket side (R-021). Live capture code is uncommitted (no SHA).
5. **Capacity:** gas winner-YES flow is about $800/day in total (15c43a29), so gas cannot reach $200/day at any fill rate.

## 5. Next steps (owner, UTC, success test)
1. IT: books logger restart, 06:45Z. Success: PID and books size growing over 60 s.
2. PK gas: R-020 fix plus power printed at the registered sigma, in the 09:30Z report. Success: a planted test where a better ask between request and response does not fill; power line printed.
3. PK gas: TinyFish runs converted to page rows, first scored day 22 Nov, 09:30Z. Success: run count, first 11/22/26 run time, one decision row, unfilled-hold count, capacity row.
4. PK sports (Dota/Goalserve threads): R-024 reads, R-022 PandaScore read, 08:00Z. Success: PID and growth for every recorder, or UNVERIFIED with the blocker.
5. PK sports: R-022 test spec for PandaScore kills vs pmcs2 own books, 12:00Z. Success: rule-to-code table, event-free placebo, plants recovered 95-105%.
6. PK: Mentions forward-test count and $/day vs $200; RN1/event-only status, 23 Nov 00:00Z (OUTBOX R-025). Success: a cited count and $/day for each, or a dated reason it was dropped.
7. Nick: whether gas continues as a stacking cell given the 103-day power (decision after the first 5 scored days).

Nothing is discarded; every row stays ranked in IDEAS.md.

Confidence 8/10: figures are from cited commits and OUTBOX rows. It is below 9 because the rows 10-12 and 13 statuses are the project's own notes from 10-11 Nov with no newer count, and the metals 0.9 bp rerun outcome was not found. To reach 9: PK's answers to R-025 and the metals rerun file.

## Update 22 Nov 05:23Z
Nick 05:22Z: gasoline dropped (rows 1-4 deprioritised; AAA TinyFish monitor paused); rebate market making moved to MFW; priority is sports feed tests, NBA included. Mentions measured: 10c rule 285 bets over 477 days, +$2,342 on $2,970 at recorded prints (average bet $10.4, limited by print size), about $4.9/day (later half about $11/day), 2.5-5.5% of $200. Depth at $200 per trade unmeasured (R-026).
