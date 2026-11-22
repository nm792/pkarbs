# SPEC (DRAFT 1, 22 Nov 04:30Z): PandaScore CS2 kills vs each token's OWN book in pmcs2. For R-022/R-023, due 12:00Z

Status: DRAFT. No code for this test exists yet; nothing below has been run. The old `it/ps_inround_test.py` results (+0.75c, UNKNOWN) are RETIRED per R-022 (map_id is a map-pool id, placebo not coded, plant overwrote itself, and I scaled the effect the wrong way). They are not evidence for or against.

## 1. Question and unit
Does a PandaScore kill (opponent alive count drops within one game_id and round) let a taker buy the favoured team's token at its own best ask, after the 1 s taker delay and our send latency, and sell at the own best bid 15 s or 60 s later for more than the fee? One decision per event, using only information at PandaScore `recv_ns`.

## 2. Data and rows
- Events: `feeds/audit_ps_inround.py: events()` then `dedup(gap=15)` (kills only for the primary; round ends reported separately). Map N = rank of `game_id` within the series (A1 of that audit); BO match-winner market gets all games.
- Prices: pmcs2 `books-*.jsonl[.gz]` rows (`recv_ms`, `asset`, `bid`, `ask`, top 3 `bids`/`asks`). Same host and clock as the PandaScore capture. Only the favoured team's token; never 1-YES.
- Entry: favoured token's own best ask in the first row with `recv_ms >= recv + 1.0 s + L`, L = send latency. L is UNMEASURED: report results at L = 0, 0.5, 1.0 s and say so. Skip event if no row within 5 s (counted, reported).
- Markout: own best bid in the last row at or before entry-time + 15 s and + 60 s (row staleness reported). Size: top-of-book depth at entry caps shares; report cents per share and shares available.
- Fee: from the market's own fee field when stored; else both 0.03 (esports, measured 20 Nov) and 0.05*p*(1-p) (docs table) are listed. Net = (bid_exit - ask_entry) - fee(entry).
- Resolution of the book clock: pmcs2 rows are change-driven (levels 2-3 at most every 10 s). Median gap between rows on the favoured token around events is reported (needed for a 1-2 s window). Windows are 1 s steps from 0 to 15 s to show the timing profile, not one 60 s window.

## 3. Statistic and inference
Primary: mean net cents per event at L = 0.5 s, 15 s markout. Inference clustered by match: per-match means, bootstrap over matches (5000), sign test over matches; within-match sign shuffle; iid p-values are not reported as evidence. Ranked estimate with interval, not pass/fail (R-023).

## 4. Controls BEFORE any real number (all must pass or the real number is not reported)
1. Event-free placebo: same entry/markout rule at random times at least 30 s from any PandaScore event, random token side, 200 draws; must read net about 0 (CI contains 0) and show the non-event move distribution.
2. Plant as RAW BOOK ROWS: inject a synthetic ask/bid step of +3c, both signs, at event recv + 5 s into a copy of the pmcs2 rows (not into the price series); the full pipeline must recover 95-105% of it. A recovery outside that band blocks the run.
3. Label swap (home/away flipped): net must be negative of fee, or about 0 before fee; must not show a lead.
4. No-edge null: replace event times with times from a different match's calendar-shifted events; must read no edge.
5. Self-overwrite guard: plant function works on a copy and a unit test asserts the original rows are unchanged.

## 5. Power and stops (computed before the run, from the first 3 matches' sigma)
Matches needed N = 2 * ((z_a + z_b) * s_m / d)^2, d = 0.5c net, s_m = between-match SD of per-match mean net. s_m is NOT known yet; it will be measured on the first matches' placebo rows (not on real events) and written to `reviewer/pandascore/POWER-ps-pmcs2-<date>.md` before any real number is read. Success stop: 95% bootstrap lower bound of net > 0 with at least 12 matches and 150 kept events. Futility stop: upper bound of net < +0.5c at 15 matches, or no matches with both tokens in pmcs2. Daily scorer on cron from the first match with both tokens recorded.

## 6. Rule-to-code table (to be filled by a thread other than the author, per Reviewer rule)
| Rule | Code location | Test that can fail | Checked by |
|---|---|---|---|
| Map N = game_id rank | audit_ps_inround.py ordinals() | test_audit_ps_inround.py | audit thread (done 20 Nov for that script) |
| Entry = first own-ask row at or after recv+1 s+L | NEW script, not written | NEW | UNCHECKED |
| Markout = own bid at +15/+60 s | NEW | NEW | UNCHECKED |
| Fee from market field, both listed | NEW | NEW | UNCHECKED |
| Event-free placebo, 200 draws | NEW (audit's A5 is on trades) | NEW | UNCHECKED |
| Plant as raw book rows, 95-105% | NEW | NEW | UNCHECKED |
| Match-clustered bootstrap + sign test | audit_ps_inround.py boot_matches/sign_test_p | existing | audit thread |

## 7. What is still missing before 12:00Z
(a) The R-022 server read (it/00-URGENT-PS-R022-...) for capture state and today's both-token match count. (b) The new scorer `feeds/ps_kills_vs_pmcs2.py` and its tests (I write it, another thread checks the table). (c) Real pmcs2 book files on this box: the scorer must run on a server export of pmcs2 hours (IT row to follow once (a) shows matches exist).
Confidence 6/10 that this design matches R-022/R-023: L unmeasured, power unknown, and no pmcs2 hours seen yet. To reach 9: the (a) read, one exported pmcs2 hour to run the plant, measured send latency.
