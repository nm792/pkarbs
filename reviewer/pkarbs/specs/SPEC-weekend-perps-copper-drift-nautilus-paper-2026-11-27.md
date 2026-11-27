# SPEC v1 (27 Nov 2026): weekend perps, two legs (A copper Sunday reopen fade, B post-open drift), Nautilus-native live paper. Written by the perps thread (R-086(3)(4), due 28 Nov 12:00Z)

Paper only, no orders ever (SETTLED A6/A7). STATUS: SPEC ONLY, nothing built. The weekend recorders (IT P138 = it/P-PERP-WKND-recorders-R086.md) are the evidence feed, not the paper node. Every $ figure is SIM or FLOOR; nothing is MEASURED until a node or recorder reads decision-time books. Both legs are UNPROVEN stack layers, each judged on its own cells (no pooling).

## 0. The two trades
- **Leg A, copper Sunday reopen (fade).** The xyz COPPER perp (Hyperliquid, HIP-3) trades all weekend; COMEX copper reopens Sun 23:00Z. If the perp moved >= 50 bp from its Friday close by T-30 min, take the position AGAINST that move at the perp's own book and exit at T+60 min. Silver and platinum ride in the same family as separate cells (metals); Brent follow is a third cell (it never earned anything on the trade as defined).
- **Leg B, post-open drift.** On Polymarket perps (api.perpetuals.polymarket.com) equity/index symbols, if the weekend mark moved >= 100 bp from Friday's cash close by T-30 min (T = the US cash open, Mon 14:30Z), enter in the signal direction at T-29..T-20 min and exit at T+5..T+10 min.

## 1. Known facts (each cited; each must hold or the node does not start)
| # | Fact | Source |
|---|---|---|
| F1 | Price each instrument from its OWN book only; the perp books and the prediction-market books are different venues | SETTLED A1; hl_weekend_logger.py, pm_weekend_logger.py |
| F2 | Leg A held-out (4 h candles, 9 bp fee per side + stressed half-spread): metals 25 signals on 14 weekends, +2 bp net (CI -84 to +104), 43% of weekends with the right sign; copper 9 signals, +71 bp net (CI -8 to +167). Rerun at 0.9 bp (Reviewer audit): metals +18.6 bp (CI -67.4 to +119.8, n 25), copper +87.2 bp (CI +7.8 to +183.1, n 9, POST HOC), Brent +41.9 (CI -252.6 to +413.4, n 7). Discovery 30 weekends: +17 bp on 1 h candles, +50 bp on 4 h: the size depends on the candle, a fragility sign | weekend-perps/RESULT-metals-brent-oos-2026-11-16.md; reviewer/pkarbs/REAUDIT-2026-11-22.md row 25 |
| F3 | Leg A capacity (live book 16 Nov ~15:30Z): copper fillable within 5 bp about $18-21k per side (OI $6.7M), platinum $20-46k, silver about $1.0-1.2M, Brent $340-360k; signals per weekend 0.4 copper, 0.4 silver, 0.3 platinum, 0.7 Brent | same RESULT file |
| F4 | Leg B on 13 weekends (Polymarket perps, trade-tape entry and exit, 8 bp round trip): 90 signals with both trades, +35.3 bp net (CI -22.5 to +95.7), 58% positive; weekday placebo -27.1 bp (CI -61.9 to +7.1); weekend minus weekday +62 bp (CI -5.6 to +133); top weekend 40.3% of net, so the locked rule is NOT PASSED. 66% of signals had no qualifying trade (thin tape), about 7 usable signals per weekend, median trade about $300 | weekend-perps/RESULT-pm-drift-and-commodity-fx-2026-11-16.md section 1; REAUDIT row 24 |
| F5 | Power: about 30 weekends are needed for leg B (13 exist) and about 18 weekends (about 4 months) for leg A at 0.4 signals per weekend | REAUDIT rows 24, 25 |
| F6 | Costs are NOT settled: the xyz taker fee is not published in the API (9 bp per side was a stress value, 4.5 bp the base, 0.9 bp the audit rerun); Polymarket perp equity taker fee 4 bp per side (/v1/info/fees). The node reads each venue's own fee at start and logs it | RESULT-metals-brent-oos (costs), LOCKED-RULE-pm-postopen (fees) |
| F7 | The weekend loggers were stopped and disabled on 23 Nov 13:30Z (T79); IT task P138 re-enables them Sun 29 Nov 22:00Z to Mon 30 Nov 15:00Z (about 26 MB/day as stored, UNVERIFIED on Prime). IT moved P138 to OPEN-WAITING.md on 25 Nov with its gates unchanged; its status was not readable to me on 27 Nov | it/P-PERP-WKND-recorders-R086.md; it/IT-2026-11-25-1600Z-P-rows-parked-load-gates.md |
| F8 | The loggers poll once per minute with 5 book levels (HL xyz: copper, silver, platinum, Brent, oil, gas, FX, equities; Polymarket perps: 11 symbols); `--interval 15` only Sun 21:00Z to Mon 00:00Z if load allows | hl_weekend_logger.py, pm_weekend_logger.py |

## 2. Rules (frozen from the locked rule files; no refit)
**Leg A** (LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md, forward version): T = the first reopen bar after the weekend gap (copper Sun 23:00Z). Friday close Pf = the perp's close at the last reference bar's end. Sown = (P_entry / Pf - 1) in bp, P_entry = the own book at the first poll at or after T-30 min (a taker price: the best ask to buy, the best bid to sell, walked to $200). Signal if |Sown| >= 50 bp. Position = -sign(Sown) for metals, +sign for Brent. Exit: the own book at the first poll at or after T+60 min. Fee and spread from the real book at each decision (F6), reported at 0.9, 4.5 and 9 bp per side.
**Leg B** (LOCKED-RULE-pm-postopen-2026-11-16.md, forward version): S = (mark at T-30 min - F)/F in bp, signal if |S| >= 100 bp. Entry: the own perp book (taker side) at the first poll inside [T-29, T-20] min instead of the tape print; exit: the first poll inside [T+5, T+10] min. The tape version stays the reference; the book version is stricter because it is an executable price. Equity cells and index cells are reported separately.
- Size: $200 per trade, never more than the own-book depth within 5 bp; cap $2,000 per weekend day. Capacity is read from the logged book at every decision, including skipped ones.
- Cells reported separately, never pooled: leg A copper, silver, platinum, Brent; leg B index, equity; leg B weekday placebo (same rule Tue-Fri).

## 3. Nautilus node (the only simulator; no custom fill or P&L code)
| Setting | Value |
|---|---|
| node | own TradingNode, trader id PKWKND-001, own paper account, own engine, own process |
| venues | OPEN QUESTION, decide at gate G2. Hyperliquid xyz perps and the Polymarket perps venue (api.perpetuals.polymarket.com) have no Polymarket-CLOB adapter; whether the pinned Nautilus version carries a Hyperliquid adapter that reads HIP-3 dexes is UNVERIFIED, and a Polymarket perps adapter is not known to exist. If neither loads: the node replays the RECORDED books as custom order-book data for an instrument definition (Nautilus matching engine does the fills; no custom fill code), and the live node waits for an adapter |
| data | L2 book deltas or the recorded 5-level snapshots for the instrument's own book, plus trade ticks where the venue offers them |
| trade_execution | True |
| queue_position | True |
| liquidity_consumption | True |
| latency | the venue's real round trip, measured at pre-flight; 0 and 1,000 ms cells offline |
| orders | marketable LIMIT at the walked own book price (IOC); no execution client |
| calendar | the reopen and cash-open times come from the venue calendar, not from hard-coded hours (DST: Sunday 23:00Z in Nov, 22:00Z in summer) |
An unsupported setting, or a venue that cannot be loaded, means the node does not start and the legs stay on the recorder plus the offline scorer.

## 4. Modelling principles (MODELLING-PRINCIPLES.md)
| s | Requirement | How |
|---|---|---|
| 2 | Power with planted edge | replay a recorded weekend with a planted +50 bp fade after every >= 50 bp move: must be detected; a replay with the move removed must be silent |
| 4 | Breadth | the independent unit is the WEEKEND (all symbols of one weekend share one regime); symbols are not independent samples |
| 5 | Shrinkage | cells ranked on shrunk mean net bp; raw counts beside it; copper's +87 bp is post hoc and is never the headline |
| 8 | No hindsight | thresholds, windows, fees and cell list frozen in a committed config before the first weekend; Pf from the venue's own Friday close |
| 10 | Fills not random | marketable IOC at the own book; the cost of the poll cadence (1 min, or 15 s) is measured against the 15 s cell |
| 11 | Regime | per month; weekend vs weekday placebo for leg B; top-weekend share of net (rule: no weekend > 40%) |
| 12 | Noise | net bp per trade after real fee and spread is primary; no hold to resolution |
| 13 | Sequential stops | blind to the first 10 weekends, then an always-valid 95% interval per cell; success lower > 0 with >= 15 signals (leg A pooled metals) or >= 30 (leg B), futility upper < 0 |
| 14 | Capacity | $/day only from measured own-book depth at decision; until then FLOOR |

## 5. Scale against the bar (F2-F5; SIM/FLOOR, not MEASURED)
- Leg A copper: 0.4 signals per weekend x $200 x 87 bp = about $0.70 a weekend; at the full 5 bp depth ($18-21k) the audit's upper bound is about $20 a week. Metals pooled is not positive out of sample.
- Leg B: about 7 usable signals per weekend x $200 x 35 bp = about $4.90 a weekend, sign uncertain (CI spans 0), tape depth a few hundred dollars per trade.
- Both are stack layers of cents to a few dollars a day; neither is close to $200/day stand-alone. What settles them: about 18 weekends (leg A) and 30 weekends (leg B) of decision-time books, so the calendar, not the code, is the limit. Recording from 29 Nov starts the clock; each weekend adds one cluster.

## 6. Start gates (none true today)
G1 recorders: IT's R-058 pre-flight for P138/P-PERP-WKND pasted and passing before Sun 29 Nov 22:00Z (COPPER present, flock lock, health_jsonl PASS, 60 s real data); P138 is in OPEN-WAITING.md, so this gate is open. G2 IT confirms the Nautilus version, each setting and the venue loading (section 3). G3 the frozen config committed before weekend 1, and the offline scorer (recorded books, per leg) built with can-fail tests (offline code, perps thread, no approval needed per R-047). G4 the planted-edge and null replays pass. G5 ONE NEEDS-NICK INBOX row for the server step (deploying a paper node on Prime is server code); default if Nick does not answer: recorder plus offline scorer only, node unbuilt.

Confidence 6/10 as a spec: the facts F2-F5 are quoted from the result files and not re-run by me; the venue question in section 3 is open; P138's real status is unknown to me. To reach 9: IT's pre-flight paste for P138, IT confirms the Nautilus version and venue loading, and the gate signs the table.
