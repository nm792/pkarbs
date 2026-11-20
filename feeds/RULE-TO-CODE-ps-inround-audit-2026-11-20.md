# Independent audit: PandaScore CS2 in-round kill lead (checker thread "Audit CS2 model", 20 Nov 2026)
Audited: reviewer/pandascore/PREREG-inround-sign-placebo-2026-11-20.md, RESULT-inround-sign-placebo-10matches-2026-11-20.md (15-match update, 93ccb99e72), it/ps_inround_test.py (84 lines, b7ed383e68 tree).
Re-run: feeds/audit_ps_inround.py (tests: feeds/test_audit_ps_inround.py, ALL PASS) on scratch/ps_samples (the same 15 exported matches), public data-api v2 trades fetched on 20 Nov 2026 in this session. Output: `ps_inround_audit_run_2026-11-20.txt` next to this file in /mnt/project-files/reviews/.
The audited script was also re-run unchanged on the same samples: n=652, LEAD +0.75c, ANTICIPATION +0.15c, 11/15, identical to the RESULT file. So the headline is reproduced; the findings below are about what it measures.
Prices are still LAST PUBLIC TRADES (and first BUY prints as an ask proxy). Own-book asks are NOT used: no pmcs2 books exist here for 19 Nov 11Z-22Z. Everything below is exploratory and carries that label.

## Rule-to-code table (PREREG rule -> code -> audit finding)
| # | PREREG rule | Code (it/ps_inround_test.py) | Finding | Status |
|---|---|---|---|---|
| 1 | Matches with in-round fields, >=30 public trades per market | `len(tr) < 30` skip; samples = IT export of top-N matches by in-round message count | OK. Export picks the matches with the MOST in-round data (long, complete matches); 1791311 is a truncated sample | OK, note selection |
| 2 | Price = last trade at or before t, outcome 0 | `px(t)` | Implemented. But the last print is old: median age 18.7 s at the event (24 s for first-kill rows); only 48% of event-market rows have ANY print in the next 15 s. LEAD is "the move visible in prints", not book repricing | OK, limits the claim |
| 3 | Markets: match winner and Map N winner, "N = PandaScore map_id at the event" | `mp != mapno` compares PS `map_id` with the N in the question | **SPEC AND CODE WRONG.** `map_id` is a map-POOL id (values 8, 31, 4, 6, 2, 1, 30 seen), not the order in the series. `game_id` rises by one per map (238558, 238559...) and gives the order. Map N rows were dropped or given another map's events | **FAIL (bug in spec and code)** |
| 4 | Exclude totals, handicaps, O/U | substring test on the question | Implemented; "spread" not excluded; any market whose outcome 0 contains a team name is admitted (audit requires outcomes == the two teams, each matched exactly once) | OK, loose |
| 5 | Kill = opponent alive count drops within the same round | `cur["rnd"] == prev["rnd"]` and same `map_id` | Implemented. `map_id` is null in some messages, which breaks the chain; audit keys on `game_id`. Counts: audit 739 kill events after dedup (market-averaged) | OK |
| 6 | Round end = score rises within the same map | same loop | Implemented; the last kill of a round IS the round end (audit adds a filter: no round end within 15 s after the kill) | OK |
| 7 | Dedup: same kind within 15 s of last kept | `ded` loop | Implemented, per kind across both teams | OK |
| 8 | LEAD = mean s*(P(t+15)-P(t)); ANTICIPATION = mean s*(P(t)-P(t-15)) | `lead`, `pobs` | Implemented | OK |
| 9 | Sign test: flip s 5,000x, p = share |mean| >= observed | `random.choice((-1,1))` per row | Implemented, but rows are event x market (1-3 markets per event, kills cluster in rounds, matches differ): p<0.0001 is not an evidence level. Match-clustered numbers below | **p NOT VALID as stated** |
| 10 | Placebo: same count of random event-free times, random sign, mean inside +-0.5c | **absent**: the docstring says it, the code has no placebo block | Not run by the PandaScore thread. Audit runs it: random time/random sign mean -0.001c [-0.06,+0.05] (uninformative by construction, random sign averages to 0); events shifted by 40-240 s keeping their sign +0.02c [-0.12,+0.17] (informative: no drift at the same sign pattern) | **MISSING in code; audit supplies it, passes** |
| 11 | Per-match mean and count of positive matches | `bym` printed | Implemented. Reproduced 11 of 15 | OK |
| 12 | >=12 matches, >=150 kept kill events | no gate in code | 15 matches, 739 kill events (audit count) | Met (checked by hand) |
| 13 | PASS: LEAD >= +1.0c, p<0.01, ANT p>0.05, >=70% positive, placebo in +-0.5c | not coded; read by hand in the RESULT file | See verdict table | see below |
| 14 | Planted +3c check on the full sample | adds prints at t+5 and t+16 on top of real prints | Recovery ~50% is mostly OVERWRITING: real prints between t+5 and t+15 replace the planted one. Audit plants by shifting the real prints in [t+5, t+16): recovery 34% (+1.01c of +3c), which matches the share of rows with a print in that window. So recovery measures print density, not the size of a real lead. "Scale the real +0.75c by 2 to get +1.5c" is NOT supported | **Plant valid for sign/detection only, NOT for size** |
| 15 | Costs: fee 0.05*p*(1-p), 1 s delay | documented, not coded | Audit codes both (A6, A7) | see below |

## Numbers (audit run, all cite feeds/audit_ps_inround.py + the output file; c = cents)
| Rows | n | LEAD | ANT | LEAD-ANT | match-bootstrap 95% of LEAD | matches positive | sign test over matches |
|---|---|---|---|---|---|---|---|
| Kills, event x market, corrected map mapping | 1006 | +0.82 | +0.63 [0.0, 1.57] | +0.18 | [+0.29, +1.29] | 11/15 | p=0.12 |
| Kills, one row per event | 739 | +0.94 | +0.72 | +0.22 | [+0.30, +1.48] | 11/15 | p=0.12 |
| First kill of each round | 344 | +0.79 | +0.67 [0.14, 1.38] | +0.12 | [-0.09, +1.47] | 9/15 | p=0.42 |
| Moneyline (series winner) markets only | 512 | +0.83 | +0.19 [-0.17, 0.74] | +0.64 | [+0.34, +1.47] | 10/15 | p=0.18 |
| Map N winner markets only | 494 | +0.80 | **+1.09 [0.04, 2.41]** | -0.29 | [-0.18, +1.54] | 6/15 | p=0.51 |
| Moneyline, no round end within 15 s | 374 | +0.87 | +0.32 | +0.56 | [+0.36, +1.57] | 10/15 | p=0.09 |

Reading: the original +0.75c / ANT +0.15c is almost all moneyline rows (512 of 652). There the kill lead is small (+0.8c) and not anticipated. In the Map N winner markets, once the right events are matched, the price moves +1.1c in the 15 s BEFORE the PandaScore message and no more after it: PM leads PandaScore on kills there, so there is no feed lead. The pooled ANT is not clean (lower bound 0.0).

## Verdict against the PREREG
- Does UNKNOWN hold? Yes. No PASS: pooled LEAD +0.82c to +0.94c is below +1.0c, ANT is not clean on the pooled or first-kill rows, and the iid p-value is invalid. No FAIL either: LEAD >= +0.5c and match-bootstrap CIs mostly exclude 0. The one cleaner cell (moneyline) is +0.83c, 10/15 matches, ANT clean, but it is below +1.0c.
- Clustering and non-independence: events within a round and markets of one match are not independent. Valid p-values are at match level: sign test over matches 0.12 (all kills), 0.18 (moneyline), 0.42 (first kill per round); bootstrap over matches CI [+0.29, +1.29]c. The within-match sign shuffle (also anticipated by the PREREG) is still anti-conservative.
- Net of the 1.25c fee and the 1 s delay: the 1 s delay costs about 0.1c (LEAD from t+1 s is +0.72c against +0.82c; the move inside 0-1 s is +0.09c). A taker pays up to 1.25c at p=0.5 (mean entry here 0.58) on a +0.8c lead: -0.4c before spread. The executable proxy (first BUY print on the favoured token at >= t+1 s, marked at the last print at t+15 s, fee on entry only) gives gross +0.09c to +0.17c and **net -0.65c to -0.98c per fill** (fill rate 45-64%). No taker edge on this evidence. Resting-order economics are untested.
- Confounders still open: trade timestamps are whole seconds and PM time vs our recv_ns clock offset is not measured (this alone can move mass between ANT and LEAD); kills of a star or in a won economy are not weighted; the sample holds the matches with the most in-round data.

## What would settle it (one-step asks)
1. Own-book asks: pmcs2 raw books for 19 Nov 11Z-22Z (storage box) or, simpler, the slim pmcs2 books from 20 Nov 05:17Z with a fresh PandaScore in-round export of >= 12 matches; then price the favoured token's own best ask at t+1 s and its own bid at t+15 s. Command is the same audit script once a books reader is added (not yet written).
2. Fix the PREREG map rule (game_id rank) and add the placebo to it/ps_inround_test.py or retire that script in favour of this audit.
3. Clock offset between recv_ns and PM timestamps (feeds/pm_recorder_lag_probe.py output) before any ANT/LEAD split is trusted.

Confidence 7/10 that the findings are factually right and the table is complete. Below 9 because: no own-book asks; whole-second trade timestamps and unmeasured clock offset; 15 matches; the execution proxy uses prints, not the book. Information needed to reach 9: the books (item 1) and the offset (item 3).
