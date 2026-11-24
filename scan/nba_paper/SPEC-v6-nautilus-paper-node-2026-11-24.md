# SPEC v6 (24 Nov 2026): NBA post-only maker paper, OWN Nautilus paper node. Resubmission after gate v5 (448c2130bd / 7a49c18640): items 3 PARTIAL, 4 FAIL, 2 conditional

Read from reviewer/pkarbs/gate/GATE-PK-NBA-maker-spec-v5-2026-11-24.md (reviewer branch). Its clear-list has 5 lines; each is answered below in the gate's own words. SUPERSEDES v5. Paper only, no orders ever (SETTLED A7). STATUS: SPEC ONLY. The node is not built and will not start until every gate in section 7 is met. Tested pieces delivered with this version are marked TESTED; everything else NOT BUILT, UNCHECKED.

## Clear-list line 1: A LIVE two-token trade-print feed for the node, named and tested (not a REST backfill, no books-only default)
- Feed, named: the Polymarket CLOB WebSocket market channel `last_trade_price` events for BOTH tokens of every game the node quotes (YES and NO token of the moneyline market), consumed through the Nautilus Polymarket live data client as trade ticks for both instruments (the client class and its trade-tick subscription on Prime's pinned Nautilus version: UNVERIFIED, IT to paste `pip show nautilus_trader` and the data-client config). The Data API v2 is NOT the node's feed (REST backfill; kept only for offline checks through pm_data_api_v2.py).
- Tested: scan/nba_paper/trade_feed_probe.js + test_trade_feed_probe.js (TESTED locally against a fake websocket: both tokens print = PASS exit 0; one token never acknowledged = exit 5; acknowledged but no prints = exit 6; no server = exit 4; a mutant that accepts one acknowledged token fails). The real websocket is blocked in my sandbox, so UNVERIFIED on the real socket until IT runs the probe during an NBA game: `node trade_feed_probe.js <tokenYes> <tokenNo> 60`.
- The books-only default is REMOVED. If the live two-token trade feed is not up, the node does not start (no 'label LOWER BOUND and run'). A runtime watchdog halts NEW orders if neither token prints for 120 s while the game is in play (NBA moneylines print far more often; a 120 s silence means the feed is down, not that the market is quiet) and logs the halt.
- P106e (books) stays as evidence for queue and markouts only; it has no prints (G1) and is not the node's feed.

## Clear-list line 2: the MINT fill-only and de-duplication rules, with the planted cases
Implemented as the executable rule file scan/nba_paper/mint_map.py with test_mint_map.py (TESTED, 15 checks, 3 mutants each fail). The file is the feed pre-processor spec and a test oracle; fills are made by the Nautilus engine, not by this file.
1. Same-token prints pass unchanged: an aggressor SELL print at or below our bid price fills our bid; a BUY print does not (planted cases).
2. OTHER-TOKEN BUYER prints are mapped FILL-ONLY: a taker BUY of the other token at price q mints against our resting BUY at p >= 1 - q, so it becomes a SELL-aggressor tick on our token at 1 - q with fill_only=True; the mapped tick NEVER reaches pricing, mid, markout or signals (planted: pricing_view returns none of them; mutant that leaks them fails). Planted: other-token BUY fills our bid with mapping ON, gives NO fill with mapping OFF; other-token BUY at 0.40 (our 0.60) does not fill a 0.50 bid; other-token SELL is never mapped.
3. De-duplicated against our own token's prints by (token, price, size, ts_event): the same trade seen on both feeds counts once (planted: 40 shares filled once, not 80; a different ts_event is not a duplicate; mutant without de-dup fails).
4. Pre-flight fail case: a post-only order accepted at or above the real own-token ask is a FAIL (post_only_ok planted at below / at / above the ask).
The engine-level versions of these planted cases (injecting the planted ticks into a test instance of the node, never the live feed) are pre-flight steps P1-P5 in section 7.

## Clear-list line 3: engine settings, named
Nautilus matching engine for the paper venue, in the node config (all must be accepted by the pinned version; a setting the pinned version does not accept = the node does NOT start, no silent default):
| Setting | Value | Why |
|---|---|---|
| trade_execution | True | fills are driven by trade ticks (the MFW trade_execution=False failure, r157, cannot recur) |
| queue_position | True | queue-ahead handling for any order that joins a level (our primary arm opens a new level, so 0 ahead) |
| liquidity_consumption | True | a trade's size is consumed once, so one print cannot fill several resting orders or fill beyond its size |
| use_message_queue | True | commands go through the venue's latency queue, not instantly |
| latency model | base latency 206 ms (measured submit-to-accept median, n=30, 5 Nov); other cells 0 ms, 250 ms (A3 hold on NBA), 1,281 ms (p90), 1,000 ms are replayed OFFLINE on recorded data with the same engine settings (the live node has one latency) | A3: hold = seconds_delay if > 0 else 250 ms |
| venue/account | own TradingNode, trader id PKNBA-001, account POLYMARKET-PAPER-PKNBA, own engine, own process | see line 3b |
| order type | post-only LIMIT only; no market orders, no execution client | A7 |
Which config classes carry these names on Prime's pinned Nautilus version: UNVERIFIED. IT pastes the node config and the version.
**3b. 'Joining the single live node' is REMOVED.** The paper node is its OWN TradingNode with its own trader id and account and engine. It may be supervised by the same supervisor, as a separate process; it never shares an account or engine with the live node (gate bucket e68e8ca3f, MFW 23 Nov). Own node/account is the ONLY arrangement.

## Clear-list line 4: the s17 table, one line per rule, with the ledger row
No file named 'ledger' exists in the repos I can read, so I use as ledger rows: SETTLED.md A-rows, MODELLING-PRINCIPLES.md section numbers, and the Reviewer order (R-) rows in INBOX. If the gate means another ledger, tell me which and I will remap; the rules and tests do not change.
| # | Rule | Ledger row | Evidence file | Test / status |
|---|---|---|---|---|
| 1 | Own-token books only; NO never from YES | SETTLED A1 | reviewer/SETTLED.md | decide on own book; YES-only book gives no NO decision; NOT BUILT |
| 2 | Hold = seconds_delay if > 0 else 250 ms; read per market | SETTLED A3; R-065; R-090 item 5 | memory nba-hold-uses-market-seconds-delay; SETTLED.md line 13 | delay.py NOT BUILT |
| 3 | Rebate per market feeSchedule on its own line; absent = UNPROVEN | SETTLED A4 | rn1-recheck README C | NOT BUILT |
| 4 | Never trade or stage orders | SETTLED A7 | SETTLED.md | post-only only; no execution client; pre-flight P5; NOT BUILT |
| 5 | No hindsight | SETTLED A8; MODELLING-PRINCIPLES 8 | MODELLING-PRINCIPLES.md s8 | decisions at receipt time; frozen SHA; NOT BUILT |
| 6 | $200/day lower-CI bar; stack layer judged separately | SETTLED A9; Nick 20 Nov (stack layers) | SETTLED.md | report line; NOT BUILT |
| 7 | No $/day without measured depth + volume at $200, $2,000/day cap | R-034 | INBOX R-034 | capacity column; NOT BUILT |
| 8 | Comparator: RN1 NBA -0.7% (3 d), own held-out -$42/game; NBA not shown positive | R-090 item 1 | rn1-recheck README E; README B | stated in section 0 of v5; kept |
| 9 | Placement: new level at best bid + 1 tick inside spread; no quote if spread <= 1 tick | R-090 item 2; gate v5 item 2 | MFW lesson (Nick 24 Nov 03:15Z) | NOT BUILT |
| 10 | Joining arm = labelled re-test of a settled finding, never a candidate | gate v5 item 2 condition A | gate v5 | arm label in every report; NOT BUILT |
| 11 | RN1 placement pull reported BEFORE any start | gate v5 item 2 condition B | scan/nba_paper/rn1_placement.py + test_rn1_placement.py (TESTED 7 checks) | not yet run: needs P106e books on Prime |
| 12 | Jump model defined with frozen SHA | gate v5 item 2 condition C | section 4 below | file SHAs listed |
| 13 | Live two-token trade feed; no books-only start | R-091 item 4a | trade_feed_probe.js | TESTED locally; real socket UNVERIFIED |
| 14 | MINT fill-only mapping + de-dup | Nick 03:33Z; R-091 item 4b | mint_map.py | TESTED 15 checks |
| 15 | Engine settings named, unsupported setting = no start | R-091 item 4c | section above | pre-flight P1-P5; NOT BUILT |
| 16 | Own node, own trader id, own account | R-091 item 4 (3b) | gate bucket e68e8ca3f | config check P6; NOT BUILT |
| 17 | NBA feed delay (free WS about 4.9-5.5 s after the play; the price is half-moved about 2.1 s after the WS frame, REVIEW-2026-11-22 line 24) | R-030/B1; winmodels note | winmodels/us/NOTE-nba-true-event-time-2026-11-04.md | measured delay must exist before any P&L is called valid; NOT BUILT |
| 18 | Order latency 0.206 s median, p90 1.281 s (n=30) | A3 / latency note | agent/outbox/nautilus-order-latency-2026-11-05.md | sensitivity cells; NOT BUILT |
| 19 | Queue measurement 6,300 shares ahead (5 min of books only) | README B | rn1-recheck README B | joining arm only; NOT BUILT |
| 20 | Power with planted edge and null | MODELLING-PRINCIPLES 2 | s2 | test_plant, null run; NOT BUILT |
| 21 | Breadth: games are the independent unit | MODELLING-PRINCIPLES 4 | s4 | cluster count; NOT BUILT |
| 22 | Shrink per cell; rank on shrunk edge | MODELLING-PRINCIPLES 5 | s5 | shrinkage table; NOT BUILT |
| 23 | Fills are not random; fill-conditional markout vs unfilled counterfactual; informed-trader check | MODELLING-PRINCIPLES 10 | s10 | flagged markout table; NOT BUILT |
| 24 | Regime: per game/day/week, top-5 share, CUSUM | MODELLING-PRINCIPLES 11 | s11 | block table; NOT BUILT |
| 25 | Noise: 10-min markout primary, 1-min secondary, settlement separate | MODELLING-PRINCIPLES 12 | s12 | NOT BUILT |
| 26 | Sequential stops: 10 blind games, always-valid 95% interval, success lower > 0, futility upper < 0, 60 game-days max then 'inconclusive, ranked' | MODELLING-PRINCIPLES 13 | s13 | stops file committed first; NOT BUILT |
| 27 | Capacity; quarter-Kelly at most, on the lower CI edge | MODELLING-PRINCIPLES 14 | s14 | NOT BUILT |
| 28 | Data API v2: valid filter asserted per row, no start/end sent, window by timestamp | R-080, P-R080-1 | scan/nba_paper/pm_data_api_v2.py | TESTED 7/7 |
| 29 | P106e books are evidence only; no prints (G1) | R-070; it/pm_sport_books.js f5be71e7f3 | recorder code | health read UNVERIFIED by me |
| 30 | Needs-Nick items go in ONE NEEDS-NICK row with a default | R-047 | INBOX R-047 | section 8 |
| 31 | Health read within 15 min of any recorder start; pre-flight before any start | R-037, R-058 | it/nba_health.sh | TESTED 6 checks |
| 32 | Paper work on Prime only | R-039 | INBOX R-039 | NOT BUILT |

## Clear-list line 5: Condition B (RN1 placement pull) and the jump model with its SHA
**RN1 placement pull.** Tool and test are done (rn1_placement.py, 7 checks TESTED, a mutant using a later book row fails); the input file (33,503 RN1 NBA maker fills, 20 Oct to 24 Nov, v2 user= with the maker/taker set difference, wallet asserted) is committed at rn1/soccer-35d-2026-11-24/rn1_nba_maker_fills.jsonl.gz. It must run against the P106e books, which exist only on Prime, so I CANNOT run it from here: RUN IT IS A START GATE (section 7), not something I claim done. Until it is reported, 'RN1 joins / improves the bid' stays UNKNOWN. IT command: `gunzip -k rn1_nba_maker_fills.jsonl.gz && python3 rn1_placement.py rn1_nba_maker_fills.jsonl /mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-23/books.jsonl.gz 0.01` (and the same for each later daily dir; fills before 23 Nov 08:58Z have no P106e books and fall into no_book).
**Jump model (defined, frozen).** From reviewer winmodels/us/nba_event.py (blob 8d100016cd): dFair = fair_after - fair_before from the normal-margin win-probability model (winmodels/us/nba_guard.py fair_at, blob 3cf61eea9c; parameters winmodels/us/params.json, blob 43f5a9ffcc: sd of remaining margin at start 14.68 for the NBA, fit on 2025-26 ESPN score paths); predicted jump = beta x dFair with beta = 0.18 fitted by through-origin least squares on TRAIN games only (39 games starting before 2026-10-28T00:00Z, 135,318 events, R2 0.06, mean |predicted| 0.74 c vs mean |actual| 1.37 c; winmodels/us/out_nba_event.txt, blob 71e611c080), then FROZEN: beta is not refit on the paper-test data. Trade only the token with predicted jump >= 1 c (MINJ 0.01) that has moved less than CAUGHT x |jump| (CAUGHT 0.5 and 1.0 as two cells). Common helpers winmodels/common.py blob 5045029858. The frozen configuration file for the paper test (beta, MINJ, CAUGHT, W, and these five blob SHAs) is committed before game 1 and its own SHA is posted. Honest read of the model: R2 0.06 means the jump model is weak; a weak model is the reason this test is a measurement and not a promise. If any of the five files changes, the cell is a new cell.

## Gate items carried unchanged
Item 1 (comparator) and item 5 (delay class) PASS as v5; text kept. Item 2 conditions: A (joining arm only as a labelled re-test) = rule 10 above, C (jump model + SHA) = above, B (RN1 pull before any start) = start gate. Open and non-blocking from gate item 1: RN1's NBA book is mostly totals and spreads (one-night maker $: totals $38.8K, spreads $22.7K, moneylines $18.4K, README A); this rule trades MONEYLINES ONLY, so RN1's NBA result is a comparator for the engine, not for this market type; a 3-day per-type RN1 P&L is not in the README and I have not computed it.

## 7. Start gates (all must be true before the node starts; none is true today)
G-a RN1 placement pull run on Prime and reported (line 5). G-b Trade feed probe PASS for both tokens of a live NBA game within 15 min before the start (line 1). G-c Engine pre-flight on a test instance: P1 planted same-token SELL print fills our bid; P2 planted other-token BUY print fills with mapping on and gives no fill with mapping off; P3 a mapped tick does not reach the mid or markout; P4 duplicate trade counted once; P5 post-only at or above the real ask is rejected. P6 config shows own trader id and account and no shared engine. G-d the pinned Nautilus version accepts every setting in the table. G-e frozen jump configuration committed and its SHA posted. G-f health read of the node and of P106e posted within 15 min (R-037). G-g needs-Nick items answered or defaulted (section 8).

## 8. NEEDS-NICK (one row, R-047; default if no answer)
What: approve running the own paper node on Prime (server code) and its live trade feed. Why: no fills can be measured without prints. Cost/risk: one extra process and websocket, disk about 10-20 MB/day for prints, no orders, no keys; if misconfigured the node idles. Default if Nick does not answer: the node does NOT start; spec stays at v6 (no books-only run).

## 9. Stand-alone vs bar and what settles it
NBA is not shown positive (v5 section 0). Stand-alone vs the A9 bar: NO. Stack layer: UNPROVEN. Settles it: measured prints at an inside level including MINT, fill-conditional markout, measured feed delay under 2 s (B1), 30+ games through the stops.

Confidence 7/10 as a spec (up from 6: the feed, MINT and RN1 tools are built and tested locally). To reach 9: IT runs the probe on a live NBA game and the RN1 placement pull on Prime; IT pastes the Nautilus version and node config; the gate confirms the ledger mapping; a second thread signs the s17 table.
