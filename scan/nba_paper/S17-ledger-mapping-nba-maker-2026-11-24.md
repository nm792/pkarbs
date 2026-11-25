# s17 ledger mapping, NBA maker paper test (R-092 C3). Extracted unchanged from SPEC v6 (7639a39ac5) clear-list line 4; posted 24 Nov 2026.

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

