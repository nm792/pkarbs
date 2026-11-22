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
