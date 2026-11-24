# SPEC v4 (24 Nov 2026): NBA maker paper = NAUTILUS-NATIVE LIVE PAPER NODE on Prime (R-081, R-077(B), R-078(1))

SUPERSEDES v3 (8f28d5e3a6) where they differ. v3's custom venue/fillsim/score code is WITHDRAWN: R-081 says NO custom fill, queue or P&L code. Paper only, no orders ever (SETTLED A7). Status: SPEC ONLY, nothing built, every row UNCHECKED until another thread signs the rule-to-code table. Basis for any $: SIM about $70/day (+$9.6/game x 7.2/day, 6 Nov sim, 5 s feed delay, 429 games; 0 s = $25.6/game, 10 s = $2.9; held-out 2026 games -$42/game at 0 s on 39 games) = SIMULATION/UNPROVEN, 35% of the $200 bar.

## 1. Architecture (what is Nautilus, what is ours)
- A Nautilus Trader strategy in LIVE mode on Prime, supervised, joining the single live node, with PAPER execution (Nautilus's own simulated execution client; it never holds a venue credential). Which Nautilus version/execution-client class Prime pins: UNVERIFIED (IT to paste `pip show nautilus_trader` and the node config). Fills, queue handling, positions and P&L come from the Nautilus engine and its portfolio/reports. We write NO fill, queue or P&L code.
- Our code is only: (a) the strategy (quote rule, section 3), (b) a market loader (Gamma NBA moneylines -> instruments, reading seconds_delay and feeSchedule per market), (c) an evidence joiner that reads P106e books offline and compares to the node's orders. (c) is analysis only and never feeds the node.
- Strategy has no real execution client; a test asserts the node config contains only the paper client (row 30). Any change to the live node is server code = ONE NEEDS-NICK row (R-047); this spec ships the strategy file and config as a proposal.
- P106e (it/pm_sport_books.js, f5be71e7f3) feeds queue-position EVIDENCE and markouts only, not the engine.

## 2. Known-facts table (each with its source)
| Fact | Value | Source |
|---|---|---|
| Books are per token; NO never priced from YES | both tokens quoted from their own book | SETTLED A1 |
| seconds_delay is per market | 0 on 2 NBA games (23 Nov 09:00Z), 1 s soccer/NHL/tennis/CS2; read per market at decision time; 250 ms is not used for sports | SETTLED A3; R-065 memory (nba-hold-uses-market-seconds-delay) |
| Post-only is not affected by the matching delay either way | Reviewer note | rn1-recheck-2026-11-24/README.md C |
| feeSchedule per market | sports_fees_v2 rate 0.03, rebateRate 0.25 on current CS2 match markets; NBA value UNVERIFIED, read per market, absent = rebate UNPROVEN and excluded | README C; SETTLED A4 |
| Minimum order | 5 shares | Reviewer order R-077(B); verify against one NBA market's order-size field (UNVERIFIED) |
| Post-only behaviour | a post-only bid at or above best ask is rejected, not filled; resting bid below the ask rests | Polymarket CLOB docs (to quote the page in the audit file; UNVERIFIED by me) |
| Order latency (live) | submit-to-accept median 0.206 s, p90 1.281 s, n=30, 5 Nov | agent/outbox/nautilus-order-latency-2026-11-05.md |
| Queue ahead | median 6,300 shares, measured on 5 min of late-game books only (main uncertainty) | README B; v1 row 13 |
| Own-token books exist | P106e live since 23 Nov 08:58Z, 20/20 tokens | Reviewer relay; HEALTH READ UNVERIFIED by me |
| Trade prints | P106e DROPS last_trade_price: no own-token prints in the books file (G1) | pm_cs2_books.js applyMsg |
| RN1 comparator | 84% maker by $, buy-only; NBA maker +10.5% on $42.5K in one night; taker -16 to -18% | README A (one night, noisy) |

## 3. Quote rule (parameters, not code)
Per game, YES and NO separately: post-only bid at floor(mid x 0.975, 0.001) of that token's own book, size max(5 shares, $200/price) with notional <= $200, 10 s life then cancel, trigger = NBA score event at feed receipt, never official time. Event-cancel window (pull bids after events) as a parameter 0, 3, 10, 30 s (README C). Hold read per market at decision time; read failure = skip and log.

## 4. MODELLING-PRINCIPLES table
| # | Principle | How this spec meets it | Test |
|---|---|---|---|
| 8 | No hindsight | Decisions use only data with receipt time <= decision time; thresholds and sigma frozen and committed with SHA before the real arm is read; held-out: first 10 games blind | row 31 import-block + frozen-file check |
| 12 | Score by markout and settlement | 1-min and 10-min markouts on the own token's best bid from P106e books (Nautilus fills give the fill time/price), plus settlement per game; rebate on its own line | plant + label swap on raw rows |
| 13 | Pre-set sequential stops | Unit = game (both tokens one cluster). First 10 games no P&L viewed. Sigma = 1.5 x baseline-arm sd frozen at game 10. Always-valid 95% interval on mean per-game real-minus-baseline markout. SUCCESS lower > 0; FUTILITY upper < 0; MAX 60 game-days then "inconclusive, ranked". Looks only at games 10, 20, 40, then every 20 | stops file committed first |
| 14 | Capacity, fractional Kelly at most | edge x fillable size: fillable = min($200, measured depth at our price incl. size ahead at placement from P106e); cap $2,000/day (R-034); sizing quarter-Kelly at most, on the LOWER CI edge, no sizing statement before a lower CI exists | depth column per decision |

## 5. Queue position and fills (G1, stated honestly)
- Fill and P&L numbers are the Nautilus engine's. How its paper matching treats queue and trade-through on NBA data is UNVERIFIED until IT pastes the config; if the paper client fills a resting bid on a touch rather than a trade-through, that is an UPPER-bound mode and must be switched or labelled.
- Queue position MEASURED from the recorder: at each Nautilus order placement, ahead = size at our price in the latest own-book row (recv_ms <= placement + latency). This is evidence beside the engine's fill, not a replacement.
- Because P106e has no own-token prints (G1), an independent check "did a print at or through our price occur" needs prints: the Data API v2 trades (section 6) fetched by condition_id, with every row asserted to the requested market. Until that exists, any fill count is labelled UPPER or UNPROVEN, never FLOOR, and no $/day (R-034).

## 6. Data API v2 (R-080/R-080a)
v1 /trades and /activity are RETIRED (HTTP 410). v2 /v2/trades pages by cursor and silently ignores unknown params; only condition_id (or condition, conditionId) filters. Delivered: scan/nba_paper/pm_data_api_v2.py (fetch_trades asserts every row's condition id equals the request, rows without the field raise, fail closed) and test_pm_data_api_v2.py (planted wrong params 'condition_ids', 'markets', 'market' MUST raise: 5/5 pass; mutation: disabling the check makes 4 fail). The node's trade check uses only this client.

## 7. Gates and what settles it
Stand-alone vs the A9 bar: NO (sim 35% of $200, UNPROVEN). Stack layer: YES candidate. Settled by: measured own-token prints at or through our price, measured size ahead, a measured feed delay under 2 s (register B1; the free WS arrives about 5 s late), 30+ games passing the stops. Health read of P106e: UNVERIFIED by me (no server access); IT pastes `bash nba_health.sh /mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-23 60`.

Confidence 6/10. To reach 9: IT pastes the Nautilus version, paper-client config and its fill mode; IT pastes the P106e health read; one NBA market's feeSchedule, order minimum and seconds_delay are read live; the post-only doc page is quoted; a second thread signs the table.
