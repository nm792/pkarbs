# Stack-layer audit: every failed, parked or "no" verdict re-read for small positive-EV edges (20 Nov 2026)

Requested by Nick (20 Nov 06:31Z): threads must not drop a possible stack layer that could add to the gasoline contracts toward $200-500/day. Rule: "fails on size" alone = PARK as a stack candidate, never discard (project memory, Nick 20 Nov 06:32Z).
Goal in one sentence: reach $200-500/day automated by stacking several small positive-EV edges, gas being one layer.
Method and limits: desk audit only, no test rerun. Sources read: `reviewer/IDEAS.md` (29 rows, reviewer branch e5648c5e04), `reviewer/SETTLED.md`, `REVIEW-2026-11-17-false-negatives.md`, `REVIEW-2026-11-18-golden-cpi-gas-false-negatives.md`, `REPLY-2026-11-20-0200Z-gas-daily-rule-for-review.md`, pipeline notes in project files (`/mnt/project-files/pipeline/`), the RESULT/NOTE files named below, and project memory. Commit shown = last commit touching that file on any branch of nm792/pkarbs (`git log --all`), not necessarily the one that wrote the number. Rows marked (unread) come only from an IDEAS.md or memory verdict line; I did not re-open the source. $/day figures are the source's own; I did not recompute them.

## 1. Where we stand today (measured only)

| layer | $/day | source | caveat |
|---|---|---|---|
| Gas daily rule v2 (listing + post-AAA) | +11.7 | reviewer/REPLY-2026-11-20-0200Z-gas-daily-rule-for-review.md, code a0839d77f2 | upper bound: every printed BUY liftable, no queue; 35 events; paper only after Reviewer clears |
| Mentions, Polymarket frozen 10c entry | about +5 (later half about +11) | mentions/audit-polymarket-2026-11-10/NOTE-audit-polymarket-mentions-2026-11-10.md, 4c583cdfcc | PASS on statistics, mostly Trump events; forward test had 0 scored events on 11 Nov |
| **Measured sum** | **about $17-23/day** | | far below $200; honest gap is about 10x |

So no combination of layers that has a measured positive number reaches $200/day today. The route is to convert the "unknown" rows below into measured ones. Combined worst-day loss, P&L correlation and shared capital are not measured for any layer (SETTLED A9 asks for them).

## 2. Top stack candidates, ranked (stack = small, positive or plausibly positive after fees, automatable)

| rank | idea | stand-alone $/day (source) | why it is a layer, what settles it | status |
|---|---|---|---|---|
| 1 | **Gas daily rule v2** (`post` rule alone +$92 over 15 days, 37/37 wins) | +11.7 (v2 all), post-only about +6 on traded days (REPLY-2026-11-20-0200Z) | Already a layer. Settle: live book at listing and at the AAA flip (depth about $1 per 30 min printed) | LIVE capture, paper blocked on Reviewer |
| 2 | **Gas winner-YES stale depth** (winner BUY prints below 0.95 before the AAA flip converges) | informed-taker pool about $37/day executed (pipeline/JUMP-SCREEN-2026-11-19.md, 34 events); winner YES about $800-920/day volume (memory gamma-volume-is-shares-not-dollars) | A floor for stale depth, not a ceiling; overlaps rank 1 (same events), do not add twice. Settle: recorded books at 03:00-11:00Z | recorder running, 19-20 Nov listing books are placeholders 0.99/0.01 x10 (memory) |
| 3 | **Mentions word base rate, Polymarket 10c** | about +5 (all 477 days), about +11 (later half) | Passes after correction, automatable, tiny. Settle: forward count of scored events; nobody owns it since 11 Nov | WRONGLY PARKED as "economically tiny"; forward test not running as far as I can see (mentions/forward-rerun-2026-11-11: 0 scored) |
| 4 | **Elon 48h tweet brackets, resting bid at listing** (RULE-elon-listing-2026-11-19) | unknown. Ceilings, ex-post and executed, not capturable: winner informed-taker pool about $190/day (JUMP-SCREEN), last-2h pool about $418/day, last-30-min about $20/day (pipeline/tweet-endgame-2026-11-20.csv) | Biggest pool on the board, volume $1.0M per event. Settle: 15 events with fills (pass bar in the rule) | LIVE capture since 19 Nov 17:07Z; pre-registered quarter Kelly; 5 min after listing books were 0.94-0.98 asks, so fills may never happen |
| 5 | **Metals / Brent / copper at the Sunday reopen** | no $ figure exists. Brent +48 bp [5, 95] (n 22, hit 100%); copper held-out +71 (-8, +167) bp, about +87 (+8, +183) at the 0.9 bp cost (weekend-perps/RESULT-pm-drift-and-commodity-fx-2026-11-16.md, REVIEW-2026-11-17-false-negatives item 1) | **Wrongly dropped on a cost error (9 bp charged where 0.9 bp applies), not on size.** Settle: rerun at the cost table; agreed 17 Nov, still not done (IDEAS row 8) | REOPEN, owner none |
| 6 | **Polymarket stock/index perps, drift after the cash open** | +35 bp net, CI -22 to +96, 13 weekends, about 30 needed (RESULT-pm-drift-and-commodity-fx, 6c9fc055cd); thin tape, median trade about $300 | Forward check on logger data each weekend (21-23 Nov was planned). Settle: about 30 weekends or a book-based test | NOT PASSED / UNDERPOWERED, owner unclear |
| 7 | **Perp vs PM SPX/SPY open contracts** | $0.18 to $1.85/day at 10% of flow, all CIs include 0 (RESULT-open-contracts-2026-11-19, 0a5c06ad7c); flow about $1.4k/day, stale flow about $63/day | Parked as layer per Nick 20 Nov 06:31Z. Settle: about 15 trading days of recorded own-token books (weekend-perps/open-contracts-2026-11-19/book_recorder.py), then quoted-ask test | PARKED; 19 Nov 14:30Z capture NOT verified; IT job P89 queued |
| 8 | **Macro-release stale-quote pickoff** (CPI/jobs/FOMC first 30 s) | $38/day at 30% capture ex-largest day; $8-21/day for a 1-3 s bot (reports/news-feeds/macro-pickoffs-12m-2026-10-26.md, b928f1f072); 41% from one FOMC day | Killed against a $50/day stand-alone rule; moved to "unproven" 26 Oct (needs hidden depth at least 1.31x printed). A stack layer by Nick's rule if sub-second. Settle: the pre-registered book capture (memory book-capture); I did not find its result | **Dropped on size; reclassify as stack candidate** |
| 9 | **SPX/SPX-open daily Up/Down maker (rebates plus spread)** | SPX daily total ceiling $8/day, SPX open $8/day, gross before adverse selection, 5% share assumed (scan/OUT-updown-mm-2026-11-11.md, 7a1a90cf40); crypto rows (BTC 15-min $129/day) belong to MFW | Tiny but automatable; adverse selection unmeasured. Settle: recorded books, compare with MFW before duplicating | PARKED, ceiling only |
| 10 | **NHL / NBA / CS2 / Dota event-only rules** | NHL about $35-140/day even with a perfect feed (live/nhl_feeds/NOTE-nhl-feed-timing-2026-11-05.md); NBA $21-184/day sim by feed lag 10-0 s (memory nba-true-event-time, PR #140), NBA dropped by Nick; CS2 about $250-300/day est., queue ignored (memory cs2-verdict, 4 Nov); Dota about $12/game at 0 s, about 18 games/day (memory dota-live-feed) | Feed-limited, not size-limited. NHL: LSports declined 19 Nov, revisit Jan 2027; P86 NHL book recorder routed, first puck 21 Nov 18:00Z. CS2/Dota: PandaScore/Goalserve trials running | ACTIVE for CS2/Dota/tennis; NHL = stack candidate, feed pending |

## 3. Full register: every failed, parked or "no" verdict

Stack layer? Y = possible, N = no positive-EV evidence, ? = unknown. "Size-only drop" flags verdicts that rest on size rather than on edge or cost.

| # | idea | source (file, commit) | stand-alone $/day (source) | stack layer? | what would settle it | status | flag |
|---|---|---|---|---|---|---|---|
| 1 | Perp vs PM open contracts | see rank 7 | $0.18-1.85 at 10% (CI incl. 0) | Y, parked | 15 days of books | PARKED, recorder unverified | size-only drop avoided 20 Nov |
| 2 | SPY daily perp hourly rule | reviewer/prototypes/perp-spy-daily/RESULT.md | $68/day CI -9 to +190, but sign-flip placebo +$64/day; tradeable notional $55/day | N (placebo makes the same money) | minute-level perp data for lag | FAIL (hourly), lag INCONCLUSIVE | lag question open (RESULT says hourly rule cannot see it) |
| 3 | SPY 5-min lag vs Yahoo | pipeline/SPY-5m-lag-RESULT-2026-11-19.md | -$15/day at 10%, CI -76 to +36; qualifying flow $2.7k/day | N | none; model edge was its own error | FAIL | no |
| 4 | Nowcast on daily Up/Down series (spx-open, spx close, meta, nvda, ...) | pipeline/LISTING-STUDY-2026-11-19.md | spx-open +3.4c +- 1.4c per share, depth $32 per decision, about $1/day | N for now ("$0 depth in 6 of 8 series") | recorded listing books | NOT A FAIL, different shape | size-only: log depth, cheap |
| 5 | qlib / LightGBM / factor mining on 148 series | pipeline/QLIB-STAGE-2026-11-19.md | +$1.28/day, CI -0.99 to +3.66, placebo 95th pct $3.99; 6 h factors did not survive rerun (0 of 624 pass BH) | N | frozen forward test (not meaningful as specified) | no signal | no |
| 6 | Late-winner scan, volume-first scan, step-1 series | scan/OUT-late-winner-scan-2026-11-11.md (2e89ce3abe), OUT-volume-first-scan-2026-11-11.md (e3b103d90b) | ceilings are hindsight, not P&L; result table "PASS only, else $0" (not fully read) | ? (unread) | feeds rank 2-4 | tool built | (unread) |
| 7 | Gas simple public signals on Kalshi (follow, entry grid, RBOB, cycle, early leader, underdog) | scan/OUT-gas-*-2026-11-11.md (c705b35932, e17ba9fa7a); REVIEW-2026-11-18-golden-cpi-gas-false-negatives.md | follow: hit 58-60% vs 50.4% mid, placebo z +3.1 to +6.1, but gap at ask -6.8c to -12c; $20/day over 11 d at $4/strike (OUT-gas-follow-test). Cycle: +13.0c (CI +6.3, +21.1), n 21 strikes / 8 events, UNPROVEN | Y in principle; Kalshi not tradable (SETTLED A6, future target) | resting-bid test at the mid; more cycle events | FAIL "at the ask only"; the signal passed | **cost verdict, not an edge verdict; resting bid never scored on Kalshi.** Polymarket gas listing rule (rank 1) already uses this |
| 8 | Gas nowcast favourite pre-AAA (no hindsight) | /mnt/project-files/gas/nowcast-favourite-backtest-and-rbob.md | pick hit 18/35; "price <= p-0.05" +$14/event pre-AAA vs "any price" -$9/event | Y (inside rank 1: `yes_fav`) | books at listing | folded into gas rule v2 | v2 per-rule caps changed +$3.9 to +$11.7/day; sensitivity to caps is a risk |
| 9 | CPI "Golden method" | reports/macro/NOTE-cpi-golden-method-2026-11-10.md (3f21e458) | none measured | ? | rebuild a statistic, test a less crowded series | PARKED (Nick 10 Nov, crowding); method UNTESTED | Kalshi-only today |
| 10 | Macro pickoff | rank 8 | $8-38 | Y | reachable-depth capture | UNPROVEN | **size-only drop** |
| 11 | News/sports feeds as scanner triggers | reports/news-feeds/news-feeds-2026-10-25.md | est. $10-25/day as add-on (memory news-feeds) | marginal | none | rejected as signal, kept as guard | borderline |
| 12 | Tweet counts, pre-listing model (Elon etc.) | forecast-edges/audit-2026-11-10/NOTE-audit-tweet-count-stats-2026-11-10.md (4c583cdfcc) | real +$809 vs placebo $178 +- $1,105, z +0.57; top 5 bets = profit | N as built; superseded by rank 4 | rank 4 books | no proven edge | Trump count source wrong (6/63), invalid row; 2-day windows not covered |
| 13 | Box office, later weekends | forecast-edges/NOTE-box-office-correction-2026-11-10.md; audit FAIL | tiny (about $949 on the first pass, withdrawn) | ? | forward test of next releases | "unknown, settled by forward test"; no owner/date | **no forward test date** |
| 14 | Netflix daily, MrBeast-style, Spotify/Billboard/app store | NOTE-netflix-deep, NOTE-mrbeast-style-markets-2026-11-10 | MrBeast about $12/day gross, about half placebo (memory mrbeast-style-markets-result); Netflix test half within placebo | N | none | NONE PASSED | no |
| 15 | Earnings beats (buy YES 0.3-0.7) and TSA/Spotify/app-store NO | forecast-edges/NOTE-forecast-edges-2026-11-10.md | +6.8c +- 3.2c test vs +1.4c train on $10.9M, 1,591 events; NO-side "ARTIFACT likely" (sum of bids 0.4-0.98) | ? | historical or live books | "Unknown, inconsistent"; I found no later work | **never followed up, not size-dropped** |
| 16 | Mirror pairs (reach vs dip, up vs down) | mirror-pairs/NOTE-mirror-pairs-step1-2026-11-11.md | none; newer half +10c z 3.3 but sign flips by year | ? | book prices, trend-fade rule | PARKED by Nick, revisit with MFW | no |
| 17 | Chess in-play | chess/NOTE-chess-sizing-2026-11-08.md | in-play notional $128k total, under $2k/day average, about $10k on best days | ? | WCC capture 24 Nov; lag unknown | PARKED | **date at risk: WCC game 1 is 24 Nov, listing check due 22 Nov** |
| 18 | Rugby (Top 14, 6 Nations 2027, RWC) | memory rugby-top14-result | $8k live volume over 4 matches, 76c median spread | ? | a market with real depth | "unknown" | no |
| 19 | Sports MECE sets, YES side | reports/sports-mece/all-hours-2026-10-25.md | +$96.93 detected in 12 h, none survives the 1 s delay; YES rescan -$302 at delay 0 | N | none | TESTED-FAIL | no |
| 20 | Sports MECE, NO side | REVIEW-2026-11-17-false-negatives items 8-10 | none | ? | score NO-token books; both-token recorders now exist (P86, pmcs2, pmdota) | COULD NOT PASS (NO tokens never recorded) | **never tested; free to score once books exist** |
| 21 | Intra-game maker with cancel-on-shock, pre-kickoff rewards | reports/sports-mece/intragame-edges-2026-10-25.md | -0.017c quiet + 0.061c rebate; $50/day needs 3-8% of maker volume | ? | books; reward programme terms (EPL legs $100/day each on 24 Oct per memory polymarket-rebates) | closed negative per Nick | **reward farming "not covered"; check current rewards** |
| 22 | Sharp books (Pinnacle/bet365) lead | live/oddspapi/NOTE-sharp-books-vs-pm-2026-11-05.md | lead 1-2 s, 4-6% of matches | N | Goalserve v2 daily look (live) | FAIL, Goalserve LIVE | no |
| 23 | TheSports T1 tennis | reviews/thesports-T1-result-2026-11-12.md | -3.4c, CI spans 0 (about 80% power for +10c) | N | rules out +10c only | FAIL | smaller edges not ruled out |
| 24 | Own CS2 win model | cs2model/NOTE-cs2-model-2026-11-10.md | none, adds nothing over price | N | none | exhausted | no |
| 25 | Valve free Dota feed | memory dota-live-feed | 0 (Valve 285-900 s behind) | N | Nick ruled out 18 Nov | OUT | no |
| 26 | NFL feed | winmodels/nfl/NOTE-nfl-feed-speed-and-value-2026-11-05.md | about $15/day upper bound at 0 s, about $0 at real feeds | marginal | none | closed | tiny size-only; park |
| 27 | LoL (Worlds over) | memory lol-bidsim, winmodels calendar note | $48-76/game, about 50 games a season month | Y in 2027 | LoL feed, season start | season off | date: 2027 |
| 28 | Perps: funding-window divergence, overshoot, metals reopen | weekend-perps RESULT-divergence-rerun (6c9fc055cd), RESULT-metals-brent-oos | liquid weekend +8.8 bp, CI -9.4 to +25.3; overshoot withdrawn as mechanical | ? | print the 1x-spread row; rerun metals at 0.9 bp (rank 5) | FAIL / owed | two reruns owed since 17 Nov |
| 29 | Fade PM after-hours stock-perp gaps at real books | LOCKED-RULE-divergence-followups Test 1 | none | ? | valid logger data | UNTESTED, logger data invalid | **IDEAS row 10, no owner** |
| 30 | NVDA perp reaction to news | agent/TASK-nvda-perp-huang-reaction-2026-11-13.md | none | ? | decide drop or test | partial pull only | **project to confirm** |
| 31 | Midterm cross-venue sets | reports/midterms/mece-edges-2026-10-25.md | one-off about $2.1k on about $102k | N | Kalshi not tradable | closed | no |
| 32 | Kalshi index early leader | scan/OUT-kalshi-index-leader-2026-11-11.md (e17ba9fa7a) | $0 / -$0.62 over 11 d, gap -17c to -29c | N | none | FAIL | no |
| 33 | Elon/other accounts (Trump TS, Cruz, WH) late-curve pools | JUMP-SCREEN-2026-11-19.md | Trump TS pool $10.8/day; dissent-at-fed $22/day at 0.02 events/day | ? | xtracker blocked from container; server poller | not tested | **cheap to add to rank-4 recorder** |
| 34 | TheSports/LSports/GRID/GSK/Statscore paid feeds | feeds/ notes | LSports: tennis EUR 150-240k/yr; NHL ceiling below EUR 5k fee; GRID fixed fee | feed-dependent | LSports revisit January 2027; GRID price pending | DECLINED / HOLD | revisit dates exist |

## 4. Flags: wrongly dropped, or dropped on size or cost alone

1. **Metals / Brent / copper reopen** (row 28, rank 5): cost error, rerun agreed 17 Nov and still open. Highest value per hour of work.
2. **Macro-release pickoff** (rank 8): killed on a stand-alone $50/day test; under Nick's stack rule it is a $8-21/day layer that needs one sub-second bot and a depth capture.
3. **Mentions base rate** (rank 3): the only statistically passed non-gas edge in the repo, labelled "economically tiny", no owner for the forward test.
4. **Sports MECE NO side** (row 20): never testable until NO tokens were recorded; they are now. Scoring it is a re-score on new books, not a new project.
5. **Gas on Kalshi** (row 7): signal passed, only taker entry failed; resting bid never scored. Kalshi trading is not open (SETTLED A6), so this is a future layer.
6. **Perp SPX/SPY open contracts** (rank 7): already parked correctly on 20 Nov. Risk: the 19 Nov 14:30Z capture is unverified.
7. **Items without an owner or date**: box office forward test (row 13), earnings beats (row 15), chess WCC capture due 22-24 Nov (row 17), PM post-open drift forward check (rank 6), fade after-hours gaps (row 29), NVDA perp (row 30).

## 5. What I could not verify

- I did not re-read every source in full: rows marked (unread), and the "stand-alone $/day" cells for rows 13, 14, 18, 26 come from IDEAS.md or memory verdict lines.
- The result of the pre-registered macro book capture (1.31x depth test) was not found in what I read.
- No daily-P&L correlation, shared capital or worst-day loss exists for any pair of layers, so the stack total cannot yet be bounded.
- All gas numbers are upper bounds (printed BUY liftable, no queue, no latency) and the v1 to v2 change (+$3.9 to +$11.7/day) came from cap choices.

## 6. Suggested next steps, smallest first

1. Rerun the metals/Brent/copper test at the 0.9 bp cost table (code exists; no new data).
2. Name an owner and a date for the Polymarket mentions forward test.
3. Score the sports MECE NO side on the new both-token recorders (pmcs2, pmdota, P86 NHL) once a few days exist.
4. Add Trump Truth Social and dissent-at-fed to the Elon listing recorder if xtracker polling is allowed on the server.
5. Verify the SPX-open book recorder with a live read before each 14:30Z open; add a daily interim scorer (Nick's 20 Nov rule).
6. Ask the Reviewer to add a "stack layer yes/no, $/day, what settles it" column to IDEAS.md so future verdicts carry it by default.

Confidence 6/10 that every figure is correct and the register is complete. Gaps to reach 9: read the (unread) rows in full, find the macro depth-capture result, and confirm owners for the unowned items. These sit inside the repo and the reviewer branch, not in public sources, so no web lookup would raise it.
