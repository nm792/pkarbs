# Rule-to-code table v2: Goalserve esports odds vs Polymarket price (author: Goalserve thread). 17 Nov 2026

Signer needed: the "Audit CS2 model" thread (NOT the author). v1 was NOT SIGNED (20 rows reviewed in reviews/SIGNOFF-goalserve-odds-vs-pm-rule-to-code-2026-11-17.md). This v2 answers each row. Code: `feeds/goalserve_odds_vs_pm.py` (v2). Amendments in writing: `feeds/AMENDMENT-goalserve-odds-prereg-2026-11-17.md`. Self test: `python3 -I feeds/test_goalserve_odds_vs_pm.py` (about 100 s, ALL PASS as pushed).

Signer: fill the last column with MATCH or DIFFERS plus the exact difference for every row.

| # | Your v1 verdict | What changed (code or written amendment) | Signer v2 verdict |
|---|---|---|---|
| 1 | DIFFERS (`ms` fallback, clock host) | `ms` fallback removed; PM rows without `recv_ms` are skipped and counted (`drops.book_rows_no_recv_ms`). `--clock-note` is now a REQUIRED argument and is stored in the output (IT must state recorder host, capture host, same chrony). | |
| 2 | DIFFERS (baseline vs consecutive) | Code now compares consecutive stored payloads (`base[k] = ph` every row). Amendment item 2. | |
| 3 | MATCH | unchanged | |
| 4 | MATCH | unchanged | |
| 5 | MATCH (real names from G1 first) | unchanged; real names to be read from the C inventory and the printed `market_names_excluded` before any relay. | |
| 6 | DIFFERS (start time, match list, silent drop) | Rematch (more than one PM market for the same names and kind) is EXCLUDED and counted (`events_ambiguous_rematch_excluded`), never paired to the first. Full `match_list` printed in the JSON. `events_rising_team_not_a_pm_outcome` counted. Start time is not available in either source: Amendment item 6. | |
| 7 | DIFFERS (silent drops) | Counters added: `book_rows_no_recv_ms`, `book_rows_one_sided`, `events_rising_team_not_a_pm_outcome`, `real_events_no_pm_baseline_at_t_minus_60` (onset now returns ok / none / nobase), `placebo_draws_no_pm_baseline`, `placebo_shortfall_matches`, `placebo_draws_missing`. | |
| 8 | MATCH | unchanged (nobase now separated from 'did not move', see row 7) | |
| 9 | MATCH | unchanged | |
| 10 | MATCH + W1 | Placebo now excludes +-2W (120 s) around any event of the match. Self-test planted 15 s lead is no longer read as 27 s (see test output: shift 5 median real lead 5.5 s). | |
| 11 | DIFFERS (a per title, b bar 4, c unstable) | (a) cells per title x bm x kind. (b) bar 4 over ALL events with lead >= 1.0 s. (c) placebo needs >= 30 onsets in >= 30 matches else 'unknown (placebo too thin)'. 20-seed false-pass measured: 0 of 20 at shift 0, 0 of 20 at no-edge. Amendment items 3-5. | |
| 12 | MATCH | unchanged | |
| 13 | MATCH | superseded by 11c (undefined placebo is now 'placebo too thin' unknown) | |
| 14 | MATCH | `--seed` defaults to 20261117; only the self test passes another seed | |
| 15 | DIFFERS (a pre-reg 5 s on real PM, b seeds) | (b) done: 20 seeds, false pass 0 of 20 (shift 0) and 0 of 20 (no-edge); planted 25 s passes 15 of 20, planted 15 s 10 of 20, reported. (a) Amended in writing, Amendment item 1: 5 s is below detection power on synthetic noise; a real-series shifted-plant run (5, 15, 25 s) is added after the first real run and reported next to the verdict. | |
| 16 | MATCH | unchanged | |
| 17 | DIFFERS (poll interval not measured; bar 4 trivial at shift 0) | `--poll-log` computes median/p90/p99 gap of consecutive esports polls from capture logs; output says 'NOT MEASURED' without it. Book resolution RES = 1.0 s printed; bar 4 now counts leads >= 1.0 s of ALL events (shift 0 no longer inflates). Amendment item 8. | |
| 18 | DIFFERS (per bookmaker) | `bm` is part of the cell key; `audit.bm_values` also printed. | |
| 19 | DIFFERS (n per bookmaker and title) | Each cell reports n_events, n_matches, placebo counts. Cell key = title|bm|kind. | |
| 20 | DIFFERS (game in progress vs pooled maps) | Each 'Map N Winner' is its own cell, Match Winner separate; nothing pooled. The Goalserve payload gives no field I have verified for 'game in progress', so each map is a separate series, as the pre-reg requires. | |

Known limitation (not a rule difference): the planted-edge detection power is about 25 s at n~120 on this noise, so most real cells will read 'no lead' or 'unknown' unless the lead is large.

Signed by: ____________  (thread name, date, time)
