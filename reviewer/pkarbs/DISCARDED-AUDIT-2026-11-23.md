# PK arbs: every discarded thesis re-judged against MODELLING-PRINCIPLES, plus the mentions mapping (Reviewer, 23 Nov 08:50Z)

Order: Nick 23 Nov 08:33Z ("what about PK arbs many wrongly discarded results together with the mentions contracts?"). Paper only. Desk audit of result files on pkarbs `reviewer` head 456f7515. No reruns, so every number below is quoted from a named file and every label is the Reviewer's.
Sources: REAUDIT-2026-11-22.md (36 rows plus the 23 Nov update), REVIEW-2026-11-17-false-negatives.md, OPEN-ITEMS.md, INBOX P-MEN-*, P-019, P-R036-1, mentions/forward-pm-daily-2026-11-22/*, shadow/run_sims.sh, it/mentions_pm_daily_scorer.py, and a live gamma read of the mention-market rules (08:45Z).

**Principle codes.** §1 = the test answers a different question (including tests that could not pass, such as NO priced from YES or NO books never recorded). §2 = underpowered. §3 = joint gates or stacked restrictions. §5 = pass/fail at a threshold instead of estimate-and-shrink. §6 = multiple-testing overcorrection. MID = midpoints used as prices. POOL = a pooled average hides the cells that carry the signal. CAP = capacity confused with edge (§14), for example print-sized bets read as "tiny edge". COST = wrong cost input. OK = the drop rests on a test that could pass.
§6 was not found in any PK verdict I read: no Bonferroni or FDR kill is on file. So no row carries §6.

**Overdue.** Nothing has been pushed to pkarbs reviewer since 05:45Z. The 06:00Z REAUDIT final table and the R-035 tweet-count and MECE results (OPEN-ITEMS 3, 4, 5) have not landed. They are chased in R-064.

## A. Ranked REOPEN list (largest capacity left to prove first; all UNPROVEN, all $ figures FLOOR or ceiling)

| rank | thesis | why it was discarded | principles broken | concrete evidence it is not dead | what proves or kills it |
|---|---|---|---|---|---|
| 1 | **Mentions, all families** (OPEN-ITEMS 1, 2) | "Statistically real, economically tiny": $4.9/day | **CAP** (each bet sized to ONE print, average $10.4), **§3** (one bet per event + first print + first hour + a single 10c cell), **POOL** (tested mostly earnings calls, 7.5% of 30-day volume; Trump is 85%), **§2** (the forward test had 0 scored events on 11 Nov, then no owner) | Kalshi audit: same-event placebo z 3.3, later half z 2.9 (audit-2026-11-10). Lifting only the "one print" restriction moved the same 30 days from +$2.00/day to **+$13.31/day (77 fills, $782 stake, z 1.2-2.0)**. Stake, not edge, is the limit. Edge-priced own-token asks on open events: Thanksgiving pardon $1,348 (best token $299), Salesforce $264, Deere $190, Dell $98. Full ladders: $98K, $48K, $22K, $38K | WS paper logger (it/mentions_pm_ws_paper.py, pre-flight 227e4ef9) on Prime: own-token asks at each decision, at $200/trade. **Not routed to IT yet** (P-MEN-1800). The Thanksgiving pardon resolves 24 Nov, so it is the next live event to catch |
| 2 | **MECE / neg-risk NO side, 3+ leg sets** (OPEN-ITEMS 4) | "Never a single arb" (Oct) | **§1 could-not-pass, twice**: NO books never recorded (shadow_logger.py subscribes to YES only), and the sim prices NO as 1 - YES bid. Reads ran on a fixed grid, not at news moments | Smoke test: lowest buy-all-NO cost **0.9945 before fees** (77 sets, 150 s). The 20 Nov own-ask rescore saw only 2-way NHL/CS2 markets (min askA+askB 1.001, 528,000 observations), and its author gives 3/10 that it says anything about 3-leg sets | Both-token recorder pm_mece_books.js (P90b) at release moments (Fed, elections, soccer 3-ways). The 17 Nov probe files are still missing |
| 3 | **Tweet / post count brackets** (OPEN-ITEMS 3) | "No proven edge": +$809 vs placebo $611 +- 508 | **§2** (CI -$529 to +$3,271), **CAP** (print-sized), **POOL** (top 5 bets = $782 of $809, so the average is 5 bets) | Event volume $271K/day (elon-tweets), $137K/day (48h). Causal floors -$2.79 and +$3.17/day are print-capped. The Trump count used the wrong source (6 of 63), so Trump is UNTESTED | Own-token asks at decision time via forward/late_books.py (NOT RUNNING); the listing-bid rule has 0 fill data |
| 4 | **NBA event-only post-only bid (RN1 clone)** (OPEN-ITEMS 8, 18) | Dormant: 0 live fills | **CAP** plus never tested: it was dropped on a simulation, never paper-run | The 6 Nov fill sim matched RN1 to about 1 point; about $70/day simulated (35%, SIMULATION label) | P106e NBA keeper (pre-flight f5be71e7, health a4744a2b) is queued first in IT's release order |
| 5 | **Macro-release stale-quote pickoff** (OPEN-ITEMS 19) | Killed against a $50/day bar at $8-38/day | **§5** (killed at a threshold), **CAP** (reachable depth never captured: the FOMC 28 Oct capture was lost), **POOL** (41% from one FOMC day, so the average is one day) | FLOOR 4-19% of $200 on print data | Book capture at FOMC/CPI/jobs releases on own-token asks. It stacks (§4): $8-38 is a layer, not a reason to kill |
| 6 | **Late-resolving deep-volume families** (OPEN-ITEMS 6) | Not discarded, but at risk on the summed sign flip | **POOL** (the summed $53/day flips across lead times) | 5 of 81 families have a 95% lower bound above 0, e.g. **wti-15m +$29/day on 38 events** | Prime rerun before 11:00Z (it/IT-2026-11-23-prime-late-leader-final.md); resolving-books recorder NOT RUNNING |
| 7 | **OddsPapi / Pinnacle sharp-book lead** (OPEN-ITEMS 13) | Lead of 1-2 s "inside the 1 s taker delay" | **§1** (judged against a 1 s delay; SETTLED A3 is a **250 ms** hold), coarse windows | A 1-2 s lead is 4-8x the real hold, on 4-6% of matches | Rescore at 250 ms on both-token books (Goalserve valid look) |
| 8 | **Copper / metals Sunday reopen** (OPEN-ITEMS 15) | Charged 9 bp instead of 0.9 bp; then "unknown" | **COST** (fixed), **§2** (needs about 20 signals, about 18 weekends) | Held-out copper **+87.2 bp, CI +7.8 to +183.1 (n 9, post hoc)**; metals +18.6 bp, CI -67.4 to +119.8 (n 25) | Forward shadow cell; no new data needed beyond the perps logger |
| 9 | **Weekend perps post-open drift** (OPEN-ITEMS 7) | NOT PASSED | **§2**, **§5**: 13 weekends vs about 30 needed | +35 bp net, CI -22 to +96 | Forward check on the P104 snapshot logger |
| 10 | **Earnings-beat contracts** (OPEN-ITEMS 19) | Folded into "forecast edges, none passed" | **POOL** (lumped with Netflix and MrBeast), never followed up | Test +6.8c +- 3.2c (train +1.4c) | Own-token books on the next earnings-beat listings |
| 11 | **CS2 event-only / PandaScore kills** (OPEN-ITEMS 10) | "No edge shown" on 20 matches; kills +0.83c "below 1.25c fee" | **§2** (firm verdict was due at 100 matches, never run), **§1** (old scorer used pool ids, no placebo), **COST to check** (the PM taker fee is 0.04 x p(1-p), at most 1.0c at p = 0.5, and A4 rebates reach 50%, so a flat 1.25c needs its source) | +0.83c per share gross | P105 read-only plant run on Prime (pre-flight P-PS-030). The PGL Major starts 25 Nov |
| 12 | **TheSports D1 Dota, NBA delay, LoL, cricket** (OPEN-ITEMS 9) | Never evaluated | Untested (§15 step 7: unrun cells are "untested", not dead) | 39/40 Dota games and 885 NBA games are captured | IT P106d box manifest, then offline scoring (P-NBA-3) |
| 13 | **Weekend fade after-hours gaps, NVDA** | Listed as FAIL/null | Untested; no test on file | none | Logger data, then a pre-registered test |
| 14 | **Rugby, tennis books, NHL** (OPEN-ITEMS 14) | Thin, never scored, or feed cost | Untested; tennis NO never recorded (§1) | Rugby: MEASURED $8K volume across 4 matches, 7 of 85 events usable | 6 Nations gate 30 Nov; NHL P86n read |

## B. Stays dead or capacity-limited (each verdict rests on a test that could pass)

| thesis | evidence | label |
|---|---|---|
| Sports MECE YES side | **YES rescan -$302 at delay 0** (shadow/run_sims.sh, delays 0,1,3,market). It already loses before any hold, so the missing 250 ms cell cannot rescue it | OK, dead |
| 2-way MECE on NHL/CS2 | 528,000 own-ask observations, min askA+askB 1.001 | OK for those markets only |
| Tennis taker-on-message (TheSports T1) | 86-99% of the move already priced; -3.4c. The +10c test was underpowered for smaller edges, but the pricing evidence closes taker | OK for taker; maker untested |
| Overshoot | Measured the venue's oracle reset, a mechanical effect | OK, withdrawn |
| Funding-window reversion at 0.9 bp; divergence | Rerun at the right fee; planted-edge checks passed; liquid +8.8, CI -9.4 to +25.3. One open cost assumption: spread = 3x half-spread | OK, dead (low priority to print the 1x sensitivity) |
| Own CS2 win model | Adds nothing over the market price (§9 benchmark test) | OK, dead |
| qlib factors, SPY 5-min lag, SPY daily perp | Placebo-matched nulls | OK, dead |
| Kalshi index early leader | -17c to -29c gap (n 36) | OK, dead |
| Daily Up/Down nowcast | Edge positive (+3.4c +- 1.4c) but MEASURED depth $32 per decision, $0 in 6 of 8 series | Capacity-limited, correctly ranked; not dead |
| Perp vs PM SPX open | MEASURED about $1.4K/day volume; FLOOR $5.3/day | Capacity-limited |
| Chess in-play | MEASURED under $2K/day volume | Capacity-limited, parked |
| Gas (PM, Kalshi), rebate MM, Kalshi legs | Nick 22 Nov 05:22Z and SETTLED A5/A6 | Off by Nick's say-so; stays on the ledger |
| Mirror pairs | Scored on history **midpoints (MID)**: newer half +10c z 3.3 vs older +0.3c. Not a valid verdict either way | Parked by Nick with MFW; flagged MID |
| Intra-game maker / pre-kickoff rewards | Closed negative per Nick; reward farming not covered | Nick's call; flagged, rewards may have changed since 24 Oct |
| Midterm cross-venue MECE | One-off of about $2.1K | Closed, one-off |

## C. Mentions contracts: what PK has done, status, gaps, and the conceptual mapping

**Done (all OFF-PRIME, read-only, public APIs):** frozen 10c base-rate rule with forward scorer (6df05db9); depth backtest since 1 Jan (FLOOR 3.3% all families, earnings calls 0.64%); open-event full-ladder vs edge-priced depth (P-MEN-1520); event-time screen over 67 events (P-MEN-1600); WS paper logger with R-058 pre-flight, 25 + 7 tests (227e4ef9).
**Status:** no MEASURED $/day. No own-token book has been recorded at any decision time. The firelog (IT P103) and the WS logger have not run on Prime; the WS logger was never entered in OPEN.md (P-MEN-1800).

| mapping element | what PK has | gap |
|---|---|---|
| **Resolution rules** | Rules are read per market. Live gamma read 08:45Z shows three rule types: (a) announcer markets resolve on the booth team only, kickoff to final play, national telecast only; (b) **count markets** ("say Referee 5+ times"); (c) period markets ("Trump says X in November", any recorded verbal mention, written posts excluded) | The scorer keys history by `norm(groupItemTitle)`, which strips digits and symbols (it/mentions_pm_daily_scorer.py:48-49). If a count market's title carries its threshold ("Referee 5+"), it pools with the 1+ word's history. **UNVERIFIED; PK to check.** Rule types (a)-(c) need separate base rates |
| **Base rate** | Per-word base rate from earlier Polymarket resolutions: q = (wins + 2·gp)/(n + 2), family prior, causal | **No transcript corpus.** New words fall back to the family prior. A transcript base rate (earnings-call transcripts; Trump speech transcripts; past booth broadcasts) would give P(word) per event type and length for words with no market history. Untested |
| **Live speech nowcast** | None. The event-time screen used the frozen listing fair: during-event **-$78.93/day, z -2.34** (anchor A); every T-6h to T-15m variant is negative | The volume is at event time ($279K in the 24 h before end). It needs a live transcript or caption feed plus a hazard model: P(said in the remaining time, given not yet said and the time elapsed), with YES snapping to about 1 the moment it is said. A different model; untested. The 250 ms hold (A3) is the speed bar |
| **Own-book ask** | Every scorer prices each token from its own book; never NO from YES | Not recorded at decision time (above) |
| **Capacity** | 30-day volume $1.48M over 59 events (Trump $1.26M = 85%, earnings $111K = 7.5%, other $105K). Full ladders $22K-98K per event; edge-priced asks about 1% of the ladder | Edge-priced depth is set by the frozen fair. A better fair (transcript base rate, live nowcast) changes which asks count as edge, so capacity must be re-measured per model, not carried over |

## D. Ledger
Every row in A and B maps to an OPEN-ITEMS row (1-22) or is added as rows 23-27 (sports-MECE 250 ms note under 13; mentions transcript base rate 23; mentions live nowcast 24; count-market pooling check 25; earnings-beat follow-up 26; untested perps legs (after-hours gaps, NVDA) 27). Nothing leaves the ledger.

**Confidence 7/10** that each fact is right, the rows do not overlap, and A plus B cover every PK verdict on file. To reach 9: (a) the 17 Nov MECE probe files (still missing); (b) PK's check of the count-market title pooling; (c) the source of the 1.25c CS2 fee; (d) the overdue 06:00Z REAUDIT final from the PK thread. All four sit with PK, not in public sources.
