# SPEC (DRAFT 1, 22 Nov 04:30Z): PandaScore CS2 kills vs each token's OWN book in pmcs2. For R-022/R-023, due 12:00Z

Status: FINAL-PENDING-CHECK (rule-to-code table awaiting a thread other than the author; sections 5-6 updated 22 Nov 12:40Z). Not run on real data. No code for this test exists yet; nothing below has been run. The old `it/ps_inround_test.py` results (+0.75c, UNKNOWN) are RETIRED per R-022 (map_id is a map-pool id, placebo not coded, plant overwrote itself, and I scaled the effect the wrong way). They are not evidence for or against.

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

## 5. Power and stops (arithmetic done 22 Nov 12:40Z)
Sigma source (planning figure only, NOT the new test's own sigma): `python3 -I feeds/audit_ps_inround.py scratch/ps_samples <cache>` pipeline (`build_rows`, mode dedup, field `post_cap` = move from t+1 s to t+15 s on public trades, one row per kill, markets averaged), run 22 Nov 12:30Z on the 15 samples (ps_sample_*.jsonl.gz, reviewer b7ed383e68 + earlier). Per-match mean (c): -0.21, 1.29, 0.58, 0.43, -0.08, 0.76, -1.58, 2.50, 0.79, 0.10, 0.03, 1.95, 1.61, 3.00, -0.78. Mean +0.69c, **between-match SD s_m = 1.22c**, median 35 kept kills per match, event-level SD 4.5c (737 rows). Caveats: trades not own-book prices, prints are stale (median age 18 s), some samples truncated; own-book s_m is expected to be at least as large (spread noise adds) and is re-measured on the first matches' placebo rows before any real number is read.
Matches needed to detect a mean net d with one-sided 97.5% / 80% power: N = ((1.96 + 0.84) * s_m / d)^2.
- d = 0.5c: (2.8 * 1.22 / 0.5)^2 = 46.7, so **47 matches**.
- d = 1.0c: (2.8 * 1.22 / 1.0)^2 = 11.7, so 12 matches.
- With 15 matches the smallest detectable effect is 2.8 * 1.22 / sqrt(15) = 0.88c. So a futility rule at 15 matches cannot work for 0.5c; the earlier draft's "upper bound < +0.5c at 15 matches" is REPLACED.
Pre-set rules: daily looks from the first day with at least 3 matches; each look reports the ranked estimate and a 99% match-bootstrap interval (multiple looks). SUCCESS: lower 99% bound of net03 (L = 0.5 s, 15 s markout) above 0, with at least 12 matches and 150 kept kills, and all section-4 controls passing. FUTILITY: at 30 matches or more, upper 95% bound of net03 below +0.5c; or no matches with both tokens' books after 7 days. HARD STOP at 47 matches: report the estimate with its interval; no pass/fail beyond that. Matches per day with both tokens is UNKNOWN until the R-022 server read; at 5/day, 47 matches take about 10 days.

## 6. Rule-to-code table (checker: "Audit CS2 model" thread, reviewer/pandascore/CHECK-ps-kills-vs-pmcs2-2026-11-22.md at 72a3cb572b; fixes A-D by the author 22 Nov ~13:15Z are AWAITING RE-CHECK)
| Rule | Code (feeds/ps_kills_vs_pmcs2.py) | Test that can fail | Checker status |
|---|---|---|---|
| Map N = game order of first appearance (all messages); Map N skipped if capture starts mid-game (D) | `series_ordinals`, `load_match` | fixture has moneyline + Map 1 + Map 2 markets (Map 2 gets no events); mid-game fixture skips Map N | code ok, test gap closed (re-check) |
| One decision per event, markets averaged (C) | `run` (per event key), `summ` | 20 events not 20 x markets | re-check |
| Entry = first own ask at/after recv+1 s+L within 5 s ('row' primary); 'state' secondary | `trade_event` | wait test, state test | CHECKED |
| Markout own bid +15/+60 s; staleness, row gap, ask size reported (C) | `trade_event`, `summ` | summary-fields test (60 s still not asserted) | partly checked |
| Fee on entry only, 0.03 and 0.05 | `trade_event` | net03 = gross - 0.75c | CHECKED; no exit fee (stated) |
| Event-free placebo; criterion = placebo gross interval contains -mean spread (B) | `run(placebo)`, `main` | placebo = -spread | re-check |
| Plant as raw rows on ISOLATED events only (A); not measurable below 5 isolated events | `plant_book`, `isolated`, `main` | 120 s, mixed 120/20 s must pass; 20 s all-events case documented as outside band; mutants (mutating input, no isolation) fail | re-check |
| Label swap below real; +300 s shift control (B) | `run(swap/shift)`, `main` | swap -5c; shift -spread; books loaded to t1+420 s | re-check |
| 99% and 95% match bootstrap; sign test; within-match label shuffle (C) | `summ`, `_boot`, `shuffle_p` | 99% >= 95% width; shuffle p small on 3c lead | re-check |
| Gate: no real number unless controls pass (C) | `main` | passes on 120 s fixture, WITHHELD at 20 s | re-check |
| Not coded (stated): depth beyond top-of-book size, exit fee, survivor split of events with no exit bid | - | - | open |

## 7. What is still missing (new due 15:00Z, R-042)
(a) The server read: IT agent stalled since 07:36Z (it/IT-2026-11-22-1020Z-pkarbs-routing.md); my read is now inside P102. (c) done as a row: it/00-URGENT-PS-P105-one-pmcs2-hour-plant-on-Prime.md. (b) DONE 22 Nov 05:00Z: scorer `feeds/ps_kills_vs_pmcs2.py` + `feeds/test_ps_kills_vs_pmcs2.py` (11 checks pass on synthetic data; a mutant that mutates its input fails). Not yet run on real data. Another thread must check the table. (c) Real pmcs2 book files on this box: the scorer must run on a server export of pmcs2 hours (IT row to follow once (a) shows matches exist).
Confidence 6/10 that this design matches R-022/R-023: L unmeasured, power unknown, and no pmcs2 hours seen yet. To reach 9: the (a) read, one exported pmcs2 hour to run the plant, measured send latency.
