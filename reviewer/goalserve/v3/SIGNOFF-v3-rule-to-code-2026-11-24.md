# SIGN-OFF of goalserve_v3_look.py against SPEC-v3 (rule-to-code table), Goalserve thread as second reader, 24 Nov 2026
Reviewer code under review: `goalserve_v3_look.py` sha256 c75edd537bffb12c50a364def548113d1658175fa6e3a4b35a4edd8505a64b09 (last commit d80a14c9ce); its test `test_goalserve_v3_look.py` sha256 3e32e99f...1838 (ALL PASS). I did not write this code (the spec is mine).
**DECISION: SIGN the code for the NHL and CS2 reads, on four conditions (C1-C4 below). The Reviewer's own test was NOT enough to sign: 6 of 7 spec-critical lines could be broken without any check failing (mutation table). I added `test_goalserve_v3_gaps.py` (sha256 89c3ff39...13e6) which kills all six; a signed run needs BOTH tests ALL PASS on the Prime copy, with the code sha above.**

## Rule-to-code table (SPEC section -> code, verdict)
| SPEC | Rule | Code | Result |
|---|---|---|---|
| 1 PM input per cell | cs2 -> pmcs2, nhl -> pmsport, tennis -> pmtennis; reader of books-*.jsonl[.gz] and books.jsonl.gz; team join by containment, drop ambiguous | `--pm` dirs; `Books.load` globs the four patterns; `name_match` (whole-word, shorter side >= 2 chars), `join()` needs both teams on different outcomes, exactly one market else counted; start within 12 h | MATCHES. Extra: 12 h start window (spec silent), harmless. Unverified: NHL league string must be exactly "NHL" (`game_of`); first Prime read prints `league_prefixes`, if "excluded:..." dominates the cell is empty and I will say so. |
| 1 capture rule | data only from the locked capture (23 Nov 17:00:11Z) | `--t-start` default 2026-11-23T17:00:11Z; completeness STOP for missing polled hours | MATCHES |
| 2 resolution | event time = our receive time, about 2 s uncertain; no lead finer than 2 s | note in output, d2 reported not read, `resolution_note` | MATCHES |
| 3 event | >= 2c move of vig-removed home probability between consecutive payloads, both open; reopen is not an event | `gs_events`: THR 0.02, baseline cleared when not valid/open; poll gap > 10 s clears | MATCHES (gap test: threshold and outage rule now have checks that fail when broken) |
| 3 statistic | d10 primary, d2, d60 on the RISING team's OWN token; mid = last row at or before x | `Books.d`, `WINDOWS=(2,10,60)`, token from `tmap[rise]`; one-sided row = mid undefined | MATCHES. Extra exclusion: needs an own-token row within +-300 s (`alive`), counted as events_own_book_silent_pm300s; can drop events in a very quiet book; accepted, counted. |
| 3 sign | d10 > 0 = price moved with the odds after | `sign_note` | MATCHES |
| 4 placebo | 10 draws, same match, no Goalserve move >= 1c within +-120 s, random token and sign; |mean| <= 0.2c else no verdict | `score_cell` plc, `PLC_EXCL_S`, `NPLC`, `TOL_NULL` | MATCHES |
| 4 plants | raw book rows, same parse path, +-1c at t+5 s, 95-105% recovery, else no number; swap plant | `Books.mid` plants (persistent shift of the last real row, re-parsed by `parse_book_row`), plus/minus/swap, `ok` band | MATCHES (same persistent-shift reading as v2 V18). |
| 4 nulls | label swap = negated mean within 0.2c; time shift +600 s = 0 within 0.2c | `label_swap_ok`, `time_shift_ok` | MATCHES |
| 5 power | first 12 matches by first usable event time = sizing block, never tested; N_MAX = min(100, ceil(6.185 sigma^2 / 0.005^2)) | `order[:SIZING]`, `nmax`, `tm = order[SIZING:SIZING+nmax]` (floor 12) | MATCHES (my own scorer floors at 13; no practical difference) |
| 6 stops | success z_eq*sqrt(n/N_MAX) >= 2.60; futility at >= 30 matches (or N_MAX if smaller): upper95 < 0 -> price first; < 0.2c -> no lead | `score_cell`: `z*sqrt(info) >= C_BM`, `ub < 0`, `ub < MIN_LEAD`, N_MAX reached closes | MATCHES the spec text literally. SPEC GAP (not a code defect): the spec has no effect-size floor, so 'lead' can be declared at, say, 0.1c. See C2. |
| 7 dependencies | capture sha = committed; recorders alive; v3 code signed; VOL2 gate | out of the script's scope (IT checks; sha in output `code_sha256`) | N/A in code; IT row must paste them |
| completeness | missing hour file while polls show capture -> STOP; truncated file STOP | `run()` STOP exits; `--allow-missing` exists (never for a real look) | MATCHES. GAP: an explicit `--t-end` later than the poll log is not refused (default t_end is safe). See C3. |

## Mutation table (Reviewer test vs gap test), run on c75edd53...
| Mutation of the scorer | Reviewer test | Gap test |
|---|---|---|
| d10 sign flipped | 3 fail | (caught by Reviewer test) |
| success uses z instead of z*sqrt(information time) | 0 fail | 2 fail |
| controls_ok forced True | 0 fail | 2 fail |
| sizing-block guard removed | 0 fail | 2 fail |
| test block includes the sizing block | 0 fail | 3 fail |
| outage threshold 10 s -> 1000 s | 0 fail | 2 fail |
| event threshold 2c -> 0.5c | 0 fail | 2 fail |

## Cross-implementation check (two codes, one synthetic world: 48 matches, 3 events each, +-3c, PM books every 5 s, noise +-0.2c)
| Scenario | Reviewer scorer, test-block mean d10 | My scorer (PR 475), mean d10 | Truth |
|---|---|---|---|
| PM follows by 3 s | +0.0296, lead, controls OK, plants 100% | +0.0296, meets bar | +0.03 |
| PM leads by 5 s | -0.0304, price moves first | -0.0304, price moves first | -0.03 |
| PM never reacts | -0.0004, no lead at 0.2c, closed | -0.0004, no lead at 0.2c, closed | 0 |
Differences kept (not defects): Reviewer requires league exactly NHL, mine none; join start window 12 h vs 36 h; own-book alive +-300 s vs mine recorder-heartbeat 30 s buckets; success: Reviewer z-only, mine z AND mean >= 0.5c AND events >= 60; price-first: Reviewer only upper95 < 0 at n >= 30, mine also z <= -boundary; hockey market name: Reviewer 'Home/Away' only, mine a wider set; name min length 2 vs 3. **Which runs for verdicts: the Reviewer's (pinned sha). Mine is the cross-check and runs on the same files; a disagreement in verdict class is reported, not averaged.**

## Conditions
- C1 Run both tests on Prime from the committed copy; paste ALL PASS for `test_goalserve_v3_look.py` AND `test_goalserve_v3_gaps.py` plus the code sha256. Otherwise the run is INVALID.
- C2 Reading rule until the spec is amended: a 'lead' verdict counts only if `test.mean_d10 >= 0.005` (0.5c, the design effect) and the test block holds >= 60 events; a lead below 0.5c is 'statistically detectable but below the design effect, not a pass'. Spec amendment A1 to the same effect is proposed (the code stays unchanged; the reader applies it).
- C3 Always pass `--t-end` only as the default or a time at least 60 s before the poll log end (the first Prime read uses the default).
- C4 First read must print and paste `league_prefixes`, `audit.counters` and `market_names_used`; if the NHL cell is empty because of the league string, I fix the spec/code reading (not the data).
Verdicts from this script stay UNCHECKED until an independent audit of the first real output (first 20 events by hand).
