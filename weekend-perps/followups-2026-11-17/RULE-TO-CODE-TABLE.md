# Rule-to-code table, independent checker sign-off (17 Nov 2026)

Checker: the "Audit CS2 model for missed edge" thread (a thread that did not write or run the code). Code read: perplib.py, analyze.py, follow23.py, eval1.py, sample_an.py, cand.py, hist.py as merged in #375 (b0dc4d7885). Rules: LOCKED-RULE-funding-window-divergence-2026-11-17.md (FW, #371), LOCKED-RULE-divergence-followups-2026-11-17.md (FU, #373), amended by LOCKED-RULE-cost-table-2026-11-17.md (CT, #375, replaces the 9 bp fee in FW and FU).
The author thread's own draft table and check are in verify-2026-11-17/ (#376). I used them as a starting point, re-read the code myself, and added the checks below. Every number labelled "live" was fetched 17 Nov 05:20-05:30Z; every number labelled "synthetic" is from planted data.

## Sign-off

**CONDITIONAL. The history tests (analyze.py metrics 1-4, sample_an.py, follow23.py Tests 2 and 3) match the locked rules as amended, once the MUST-FIX items below are done. Test 1 (eval1.py) must not be run for a verdict until M1 and M5 are fixed.** Items marked DECLARE need one sentence in the write-up and no code change. Nothing here changes a threshold, event definition, window, bootstrap size or seed.

## Rulings on the four AMBIGUOUS rows the coordinator asked about

| Row | Ruling | Reason |
|---|---|---|
| 0.9 bp fee against the rule's 9 bp | **MATCH to CT, with a condition.** The rule text of FW and FU still says 9 bp, but CT (merged 05:18Z) explicitly replaces it. The author's draft said "the rule file itself was not amended"; that is out of date. Condition: CT was written after the first (9 bp) results had been seen, so it is not pre-registration clean and it can only lower costs. Print the 9 bp version of every verdict cell beside the 0.9 bp one (xyz growth-mode assets only; one extra column) and say so. | See the fee evidence below: 0.9 bp is correct for growth-mode xyz on live fills, so the amendment is right on the facts. |
| Weekend-only indicator in Test 3(d) | **ACCEPT, DECLARE.** FU says "an hour-of-day/weekend indicator"; read as "or". Write "weekend indicator only, no hour-of-day term" in the result. Also fix a one-hour misalignment (M8). | "/" is ambiguous; the weaker reading is defensible and cheap to state. |
| Persistent subset taken from the primary event stream | **MATCH.** FU says "Subsets: ... (c)". A subset of the primary non-overlapping stream is the literal reading. DECLARE the window: hours h, h-1, h-2 (entry hour plus two before, all >= 100 bp same sign). "3 consecutive hours before entry" could also mean h-1..h-3; not used. | Literal reading. |
| Test 3(c) regressor | **DEPARTS, MUST-FIX (M3).** FU says "the premium before the reset". The code uses the last hour of the run (f23:74), which equals the hour before the reset only when the reset is the very next hour. Use abs(P[reset_t - H]). Keep the last-run-hour version as a labelled secondary line. | Literal reading. The author's own planted case gave slope 0.5 (code) against about 0.16 (literal). |

## Cost table: every term and what I verified (live)

| Term | Value | My check | Status |
|---|---|---|---|
| Polymarket perp taker fee | 4 bp | `GET /v1/info/fees` taker_fee_rate 0.0004 at $0 30-day volume; `GET /v1/info/fees?instrument_id=N` for all 38 equity and all 6 index perps: every one 0.0004; instrument `fee_override` is None for equity, index and commodity (only pre_ipo has an override, 2 bp, not logged). | **VERIFIED** (stronger than CT: index perps were not covered by the generic schedule, the per-instrument call covers them) |
| Hyperliquid base perp taker | 4.5 bp | `userFees` for a zero-volume address: userCrossRate 0.00045. | **VERIFIED** |
| HIP-3 builder dex x2 and growthMode x0.1 | 0.9 bp growth-mode xyz | Meta shows deployerFeeScale "1.0" on every xyz, flx and km asset and growthMode "enabled" on xyz 132 of 145, flx 12 of 16, km 20 of 23 (matches CT). Docs hosts are blocked from this container, so the formula itself is not read. **Independent check from public fills (userFillsByTime, crossed fills, last 3 days):** growth-mode xyz:NVDA taker fee 0.86 bp (98 fills), xyz:SP500 0.86 bp (153 fills); other accounts lower (0.29-0.31 bp, volume tiers); 0.86 = 0.9 x (1 - 4% referral discount). Non-growth xyz:GOLD: 9.0 bp (5, 2 and 215 fills; one account 3.92 bp with a discount). So 0.9 bp (growth) and 9 bp (non-growth) are right for a standard account, and the doubling holds. | **VERIFIED from fills for xyz** (no longer "unverified from docs"). Upgrade xyz:GOLD from COST UNCHECKED to verified at 9 bp. |
| flx and km fees | 0.9 bp if growth else 9 bp | No flx or km taker fills found in the recent trades I sampled, so not checked. | **COST UNCHECKED, correct as labelled** |
| Spread (history tests) | 3 x live l2Book half-spread, floor 1 bp | Code reads l2Book at fetch time (cand.py:11-15) and excludes symbols with no book (never defaults). The 3x is a stated stress assumption. | measured, assumption flagged |
| Test 1 spread | VWAP of $1,000 through the recorded book | Live Polymarket book format checked: `{instrument_id, bids, asks, timestamp, sequence}`, levels `["px","sz"]`, bids descending, asks ascending (47-48 levels, so the logger stores the full book, not 10). eval1's `fill()` run on a live SP500 book: $1,000 VWAP 0.07 bp from mid each side. | **VERIFIED format** |
| Hyperliquid funding | record by record | fundingHistory record times are top-of-hour plus a few ms (7, 24, 68 ms), so `time // H * H` aligns each record to the hour it settles. Rate units are fractions per hour (0.0000163 = 0.16 bp). | **VERIFIED** (sign convention is the venue's standard, not read from docs) |
| Polymarket funding (Test 1) | `/v1/info/funding?instrument_id=N` | Fields `funding_rate` (fraction) and `timestamp` (ms, top-of-hour plus ms), as eval1 parses them. **The endpoint returns only the last 24 hourly rows** (`more: false`); the parameters limit, start_time, end_time and before are ignored. | **PARTLY: see M5** |

## Planted-edge / no-edge check (synthetic)

verify-2026-11-17/checker_planted_edge_test.py runs the real scripts unchanged on two synthetic worlds (15 symbols, 24 weeks of hourly history, plus 3 symbols x 4 days of 5 s logs). EDGE world: price moves 60 bp back toward the oracle in the hour after |premium| >= 50 bp, and the perp candle moves 0.5 x |premium| toward the oracle in the reset hour; the gap in Test 1 closes through the perp price. NO-EDGE world: same divergences, but the oracle/index moves to the perp and the perp price does not move; funding is negligible. Result: **14 of 14 checks pass.** Edge world: metric 4 tradable (net about +55 bp = 60 - 7.8 cost + funding), Test 2 PASS, Test 3 slope 0.50 and ex-post bound net +228 bp, Test 1 PASS (gross 46, net 38 bp). No-edge world: metric 4 net about -7 bp (= -cost), Test 2 no PASS, Test 3 slope 0.02 and net -6 bp, Test 1 PRELIMINARY with gross -2 and net -10 bp (= -2 - 8 fee). The per-symbol fee path (0.9 bp growth: cost 7.8 bp at 1 bp half-spread) and the 4 bp x 2 Polymarket fee both show up at the expected size. A first draft of the no-edge world let funding carry make it profitable (funding = premium/8 per hour); the scripts correctly reported that carry as an edge, and I made funding small. The author's own planted check (42 PASS, 0 FAIL, verify-2026-11-17/run.log) was read but not re-run.
Bootstrap: `boot()` agrees with an independent loop implementation (95% CI (-0.2, 5.0) against (-0.3, 5.1) on 471 clustered items). Caveat: the percentile bootstrap with about 12 weekly clusters covered a true mean of 0 only 88% of the time in 300 simulations, so "CI lower bound > 0" is somewhat easier to meet than 95% nominal. DECLARE in every result that uses it.

## MUST-FIX before any verdict is relayed

| # | Where | Problem | Fix |
|---|---|---|---|
| M1 | eval1.py:8 | FU: "evaluation uses only the sessions recorded after this rule is merged". The code globs every file in LOGDIR; no time filter. | Add `--after EPOCH` and drop records with t < EPOCH. #373 merged 02:09Z (epoch 1794881341); the logger book-coverage fix #374 merged at 02:12:36Z (commit time), so use 02:13:00Z = 1794881580 and print it. |
| M2 | analyze.py:48, follow23.py:37, :80 | CT: "the sourced-only subset (growth-mode xyz) is the one that can carry a verdict". The code prints tradable/PASS over all trades and only labels how many were COST UNCHECKED. | Compute n, net, CI and the PASS flag on the checked trades only (chk True), print them as the verdict line, and print the all-trades line as "COST UNCHECKED, not a verdict". |
| M3 | follow23.py:74 | Test 3(c) regressor (see ruling above). | x = abs(P[reset_t - H]); keep last-run-hour as a secondary line. |
| M4 | follow23.py:96-101 | If there are no Test 3 episodes the logistic block crashes (IndexError, found by the author's check) after all other output. | Guard `if len(trn) and len(tst)`. |
| M5 | eval1.py:17-26 | The funding endpoint serves only the last 24 hourly rows. Any session older than 24 h at run time gets no rates; missing rates are counted but added as 0, and the verdict does not look at the count. | Either have the logger poll `/v1/info/funding` hourly and save it, or run eval1 within 24 h of the last session. Print the share of crossings with no rate and treat a PASS with any missing rate as PRELIMINARY. Effect is small (holds are about 5 min, so about 8% of trades cross an hour, funding about 1 bp) but the verdict rule should not depend on it silently. |
| M6 | pl:load_growth, cost table | growth.json (the fee map) has no committed producer and is not in the repo. Without it fee_info silently falls to 9 bp and COST UNCHECKED for every symbol. | Commit the script that writes growth.json from `meta` for xyz, flx, km (I fetched the same flags, so it is a few lines) and the file as run, with its fetch time. |
| M7 | eval1.py:62-73 | Sample spacing is not checked. The logger fetches a book per hot symbol sequentially, so a poll can take longer than 5 s; the code treats consecutive samples as 5 s apart (the "5 s latency" assumption). | Skip and count any entry/exit pair where the spacing exceeds 7.5 s, and print median and max spacing. |
| M8 | pl, follow23.py:95 | Small items: `is_weekend(nxt - H)` classifies the hour by its end time (one hour late at the boundaries; `sess()` uses the start); follow23.py:23 and :78 silently count a missing funding record as 0; perplib.py comment cites COST-TABLE-2026-11-17.md but the file is LOCKED-RULE-cost-table-2026-11-17.md. | Use `is_weekend(t - H)`; count and print missing funding records; fix the filename. |

## DECLARE in the write-up (no code change)

- Extra cells beyond the rule: Test 2 also prints (dex x tier) cells; cells with fewer than 50 hours (analyze.py:37) or 10 events (follow23.py:35) are not printed. Say the extra cells are exploratory.
- Test 1 "event-cluster": the code resamples (symbol x session) groups, which is coarser and more conservative than resampling events. State it.
- Test 3(a) merges flx and km into one group; metric 3 mean funding received is conditioned on |premium| >= 25 bp; AR(1) is a pooled correlation; run lengths are assigned to the session of the first hour.
- Metric 5 "reverts before the next top of the hour" is "reverts within the 30-minute sample" (the sample ends before the next hour).
- Universe for Tests 2 and 3: xyz needs OI > 0 but flx and km are kept with OI 0 (as "thin"); the rule fixes neither.
- History window: candles cover 208 days, funding history 420, so trades only exist where both do.
- Test 1 gate for the verdict follows eval1.py:111 exactly (>= 30 events, >= 2 days, mean net > 0, CI lower > 0, mean net > placebo mean).

## Rule-to-code summary (detail in the author's draft table and my checks)

| Rule clause | Code | Status |
|---|---|---|
| FW A: >= 60 days (1440 hourly records), OI terciles, same cut-offs everywhere | pl:universe, make_tier | MATCH (plus the OI > 0 filter, DECLARE) |
| FW session classes | pl:sess | MATCH (hour start used) |
| FW M1 median / p90 / p99, shares >= 25 and >= 50 bp | an:36-40 | MATCH |
| FW M2 persistence, AR(1), run length | an:14-17, 24-31 | MATCH (AR(1) pooled, DECLARE) |
| FW M3 funding size and fader's funding | an:13-15 | MATCH (conditioned, DECLARE) |
| FW M4 reversion trade, candle close h to close h+1, funding of hour h+1, costs per CT | an:18-23 | MATCH |
| FW M4 bootstrap weekly clusters, 10,000, seed 1; tradable rule | pl:boot, an:47-48 | MATCH (algorithm verified; coverage caveat; sourced-only subset is M2) |
| FW M5 per-symbol max |mid-oracle|, max |mark-oracle|, seconds to < 5 bp, share reverting | sa | MATCH (within the sample, DECLARE); sample-B tiers NOT IMPLEMENTED (report only) |
| FU Test 1 gap, signal, entry sample, 15 bp check, VWAP $1,000, exit rule, funding, 4 bp x 2 | e1:38-87 | MATCH |
| FU Test 1 sessions after merge | e1:8 | **NOT IMPLEMENTED (M1)** |
| FU Test 1 placebo (same symbol and session, |g| < 10, random direction, seed 1) and decision rule | e1:97-111 | MATCH |
| FU Test 2 event, position, k = 6, funding of 6 settlements, non-overlap, subsets (a)(b)(c), PASS rule | f23:13-38 | MATCH (c window DECLARE; missing funding M8; sourced-only M2) |
| FU Test 3 episode, reset, hazard, ex-post bound | f23:40-87 | MATCH |
| FU Test 3(c) regressor | f23:74 | **DEPARTS (M3)** |
| FU Test 3(d) logistic regression, 70/30 weeks, AUC | f23:89-106 | weekend only (ruling above); crash guard M4 |
| FU Test 3 "what the venue settles against" | none | write-up statement, not code |
| CT every cost term with a source | perplib, LOCKED-RULE-cost-table | VERIFIED above (flx/km UNCHECKED; growth.json producer M6) |

**Confidence: 8/10** that this table is complete and correct. What would take it to 9: re-run the four scripts on the real hist.json and cand.json after M1-M8 land and confirm the output format and cell counts, and a read of the trade.xyz and Hyperliquid fee docs (blocked here; the fills check covers the numbers but not the stated rule).
