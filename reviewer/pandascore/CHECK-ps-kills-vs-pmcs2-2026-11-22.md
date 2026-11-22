# CHECK (checker thread "Audit CS2 model", 22 Nov 2026 ~12:50Z): rule-to-code table, feeds/ps_kills_vs_pmcs2.py at reviewer 72a3cb572b
For R-042. Author: PandaScore thread. Checker: a different thread. Method: ran `python3 -I feeds/test_ps_kills_vs_pmcs2.py` (12 checks, ALL PASS), read the code against SPEC section 6 and sections 1-5, then ran the test with the fixture's kill spacing changed (mutation of the fixture) to see which rules the tests can fail on.

**Result: the 12 tests pass, but the plant control (rule 6) is NOT valid on real event spacing, and four spec rules have no code. The scorer must not be run on real data for a reported number until items A-C below are fixed. Confidence 8/10 on these findings (code read and one fixture run; no real pmcs2 data seen).**

## Table (Checked by = checker thread, 22 Nov)
| Rule | Status | Note |
|---|---|---|
| Map N = game_id rank | CHECKED, code ok, **test never reaches it** | `ordinals()` is built from game_ids that HAVE events, so a capture that starts mid-series gives Map 1 the rank of the second map. The fixture has one BO3 moneyline market, so the Map-N filter line in `run()` is never executed by this test file. |
| Entry = first own-ask row at/after recv+1 s+L, within 5 s; state variant | CHECKED | Code matches. `row` entry is the first row AFTER the decision time, so it pays the post-move ask (conservative for the taker); `state` (last row <= T) is the faithful fill at T. Both are reported; say which is primary. Tests: 5 s wait, state. |
| Markout = own bid at +15/+60 s | CHECKED (15 s only) | `state(T+h)`, T = decision time, matches the spec. +60 s is not asserted by any test. `age` (staleness) is computed but never summarised, though SPEC section 2 says staleness is reported. Events with no exit bid are skipped and not split by reason: if the favoured token's bid vanishes after a kill the mean is conditioned on a bid existing (survivor bias). |
| Fee 0.03 and 0.05*p*(1-p) | CHECKED | Fee on entry only (spec formula); no exit fee, so an exit as a taker is flattered by one fee. Only net03 is asserted; net05 is not tested. |
| Event-free placebo (30 s clear, random side) | CHECKED as code; **control as worded cannot pass** | Code matches. On real books the gross reads about minus the spread by construction, so SPEC section 4.1 "net about 0 (CI contains 0)" will fail on every real run. Compare real minus placebo, or placebo vs minus-spread, and state that. Code reports draw mean and sd only, no CI. The fixture book is constant, so the test cannot detect drift. |
| Plant as raw book rows, recovery 95-105% | **NOT VALID on real spacing** | Rows copied, original unchanged (tested). But each plant lasts 25 s (t+5 to t+30); dedup only separates kills by 15 s, so an event 15 to 28 s earlier has its plant tail inside THIS event's entry row. I ran the test with kill spacing 120 s, 40 s and 20 s: recovery 100%, 100%, **195%** (FAIL). With same-team streaks it goes toward 0%. The fixture spaces kills 120 s, so it cannot fail on this. Only the 15 s markout is planted. |
| Label swap control | CHECKED | Reads -5c on the lead book. |
| +300 s shift control | **UNTESTED, differs from spec** | No test calls `mode="shift"`. SPEC 4.4 says another match's calendar-shifted events; code shifts the same match +300 s. Books are loaded only to t1+180 s, so shifted events near the end of a match read missing rows and are skipped or stale. |
| Match-clustered bootstrap + sign test | CHECKED (re-used from audit, tested 20 Nov) | Code reports a 95% interval; SPEC 5 success rule needs 99%. The within-match sign shuffle in SPEC 3 is not coded. |

## Rules in the SPEC with no code (cannot be checked)
1. One decision per event (SPEC 1): `run()` makes one row per event x market (moneyline plus Map N), so events are counted twice and "150 kept kills" would count rows.
2. Depth at entry / shares available and top-3 levels (SPEC 2): `load_books` reads bid and ask only.
3. Median gap between rows on the favoured token around events (SPEC 2): not computed.
4. Gate: SPEC 4 says no real number is reported unless all controls pass; `main()` prints everything regardless.

## Needed before the first real number (one step each, for the author)
A. Plant only events with no other kept kill within 30 s before and 15 s after (or thin them), report recovery by spacing, and add a test with 20 s spacing that must pass. Re-run my fixture change as the failing case first.
B. Fix the placebo criterion wording and add a CI; add a test for the shift control; load books to t1+400 s or drop shifted events past t1.
C. Dedup to one row per event (or say event x market and drop "150 kills" for rows); add the 99% interval, the within-match shuffle, staleness, row gap, and the control gate.
D. Build `ordinals` from the series (first game_id seen, `not_started` rows) or skip Map N markets when the capture starts mid-series; add one Map-N fixture.

I did not edit the author's files. Test command and result: `python3 -I feeds/test_ps_kills_vs_pmcs2.py` ALL PASS (12). Fixture mutation: `sed "s/t += 120/t += 20/"` on that test, run as a copy, fails the plant check (recovery 1.95).

---
# RE-CHECK (22 Nov ~13:00Z) at reviewer e3e493d08a
Ran `python3 -I feeds/test_ps_kills_vs_pmcs2.py` on that tree: ALL PASS (24 checks). Read the new `ps_kills_vs_pmcs2.py` (about 250 lines) against SPEC 1-6 and my items A-D.

**Verdict: A, B (shift end artifact, CI), C (one row per event, 99%, staleness, gap, ask size, gate) and the Map-N fixture are FIXED and tested. I can sign the table rows below. Four rules remain untested or only partly covered, none blocks a run on the P105 plant hour; the first two decide whether the gate can ever pass on real books. Confidence 8/10.**

| Rule | Status 22 Nov 13:00Z |
|---|---|
| Map N by game order | CHECKED for mid-GAME start (round_number > 2 skips Map N, tested). **Residual, untested:** a capture that starts at round 1 of a LATER map (mid-series) passes the check and gives that map rank 1. Use the series score or the first `not_started` game_id, or restrict Map N to samples whose first message is before game 1. |
| Entry row / state, markout 15 and 60 s, fee on entry | CHECKED; 60 s now summarised but still no assertion on its value; exit fee and no-exit-bid split are stated as not coded (agreed). |
| Plant on isolated events | CHECKED. Isolated = no other kept kill -30/+15 s; tests at 120 s (100%), 20 s all events (196.7%, documented), 20 s isolated (not measurable, gate fails), mixed 120/20 s (100% on 15 isolated). Covers only the 15 s markout and only isolated events, as stated. |
| Placebo and shift gate | **Untested on variable spreads.** The gate asks that minus the mean spread AT EVENT TIMES lies inside the placebo draw interval (+-0.05c) / the shift match-bootstrap interval. The placebo interval is only the spread of 200 random draws over fixed data, so it is narrow; real spreads at random times differ from spreads at event times, so the gate can fail with no edge. The fixture has a constant spread, so no test can show this. Compare each control with minus ITS OWN mean spread (placebo rows' own spread), or run the gate once on the P105 hour and read the numbers before trusting it. If it blocks, that is a design flaw, not an edge. |
| Label swap below real | CHECKED. |
| Within-match shuffle | Coded as an independent per-event flip between the real and the other token (2000 permutations), not a shuffle inside rounds. It ignores clustering, so it is NOT evidence; the match bootstrap and sign test are. State that in the result. |
| Placebo rows | Placebo times are drawn separately for each market, so placebo events are not one row per event (3 markets give 3 times the rows). Mean unaffected; counts and match weights are. |
| Real file schema | **Untested against a real pmcs2 row.** Field names (`recv_ms`, `asset`, `bid`, `ask`, `asks[0].size` as a dict, best level first) and markets.jsonl keys (`q`, `outcomes`, `tokens`) come from the author's fixture. One real row and one real markets.jsonl line from the P105 hour must be pasted into a test before the first real run; if `asks` levels are lists or worst-first, ask size is wrong without any failure. |

Not edited: the author's files. Test command: `python3 -I feeds/test_ps_kills_vs_pmcs2.py`.
