# Rule-to-code table: Goalserve esports odds vs Polymarket price, locked rerun v2 (author: Goalserve thread). 17 Nov 2026

Signer needed: the "Audit CS2 model" thread (NOT the author). Rules: feeds/PREREG-goalserve-odds-vs-pm-v2-2026-11-18.md. Code: `feeds/goalserve_odds_vs_pm_v2.py` (imports `counted_lines`, `market_kind`, `num`, `med` from the signed v1 file feeds/goalserve_odds_vs_pm.py at 1cb5c847 and `norm`, `find`, `load_pm`, `mk_index` from feeds/ps_lead_test.py). Self test: `python3 -I feeds/test_goalserve_odds_vs_pm_v2.py` (about 3 minutes, ALL PASS as pushed).
Signer: fill the last column with MATCH or DIFFERS plus the exact difference for every row. Check each row against the code, not against this text. No silent defaults.

| # | Rule | Code | Signer verdict |
|---|---|---|---|
| 1 | Markets: only 'Home/Away' and 'Home/Away (map N)'; all others excluded and counted | `open_events`: `market_kind(name)`; `excl[name]`; `market_names_excluded` in audit | |
| 2 | Valid and open: exactly 2 participants, market and both participants not suspended, value_eu numeric > 1; each failure counted | `open_events`: `skip_not_2_participants`, `skip_suspended` (`OPEN` tuple), `skip_bad_odds` | |
| 3 | Participant to team: exact normalised team name, or '1'/'home', '2'/'away'; else excluded and counted | `open_events`: `side` list, `excluded_participant_mapping` | |
| 4 | p_home = (1/o_home)/(1/o1+1/o2) | `open_events`: `ph` | |
| 5 | Event = |p_home - previous valid-open payload value| >= 0.02; rising team = direction | `open_events`: `base[k]`, `THR`, `ev.append(...)` | |
| 6 | Baseline CLEARED when (event, market) is missing, suspended or invalid in a payload, so a reopen is never an event; counted | `open_events`: `valid` set, `del base[k]`, `baseline_cleared_not_valid_open` | |
| 7 | Cell = league prefix (text before first ' - ', normalised; none = 'unparsed') x kind; prefixes printed | `open_events`: `game`, `league_prefixes_seen`; `cells["%s|%s" % (game, kind)]` | |
| 8 | PM market = exact normalised outcome names AND kind; none or more than one (rematch) excluded and counted | `main`: `sel`, `ml`, `events_no_pm_market`, `events_ambiguous_rematch_excluded` | |
| 9 | PM book row: time = `recv_ms` if present else `ms`; token = `tk` or `asset`; mid = (max bid + min ask)/2; one-sided rows dropped and counted | `main` books loop: `tms`, `tk`, `book_rows_one_sided` | |
| 10 | At most CAP=40 events per (game, kind, match), seeded random choice; drop count reported | `main`: `CAP`, `rnd.sample`, `events_dropped_by_match_cap` | |
| 11 | R = (mid(t+60)-mid(t)) - (mid(t-5)-mid(t-60)); mid(x) = last row at or before x; no mid = dropped and counted | `R`, `mid_at`, `events_no_pm_baseline_at_t_minus_60` | |
| 12 | Rising team's OWN token only; if the rising team is not a PM outcome, dropped and counted | `main`: `outs.index(rise)`, `events_rising_team_not_a_pm_outcome` | |
| 13 | Recorder alive: a book row of either token within +-300 s of t, else dropped and counted | `alive`, `events_pm_recorder_silent_pm300s` | |
| 14 | Placebo: same t, 10 draws, random token, random sign; d = R_real - mean placebo R; none usable = dropped and counted | `main`: `NPLC`, `rnd.choice`, `events_no_placebo` | |
| 15 | Cell statistic = mean over matches of per-match mean d; CI = match-clustered bootstrap 2000, seed 20261118 | `main`: `md`, `boot`, `SEED` | |
| 16 | Bar: >= 12 matches, >= 60 events, mean d >= 0.005, CI lower > 0, share R_real > placebo mean >= 55%; CI upper < 0 = PM moved first; else no lead detected | `MIN_MATCHES`, `MIN_EVENTS`, `MIN_EFFECT`, `MIN_SHARE`, verdict block | |
| 17 | Power check: d - md + 0.01 must meet the same bar (CI lower - md + 0.01 > 0, share >= 55%), else 'unknown (underpowered)'; min_detectable_effect = md - CI lower printed | `plant_ok`, `PLANT_C`, `min_detectable_effect` | |
| 19 | Row 9 fix (checker DIFFERS): book rows with no time are dropped AND counted; the time source (recv_ms or ms) is counted | `main` books loop: `book_rows_no_time`, `pm_book_rows_time_from_recv_ms`, `pm_book_rows_time_from_ms` | |
| 20 | G2: `--poll-log` required; a payload with no poll in the preceding 10 s clears all baselines, counted | `load_polls`, `open_events`: `OUTAGE_S`, `baseline_cleared_poll_gap_gt_10s`, `payloads_after_poll_gap_gt_10s` | |
| 21 | G3: primary cells cs2|Match Winner and dota2|Match Winner; all others labelled informational, verdict prefixed '(informational)' | `PRIMARY`, cell `role`, verdict prefix | |
| 22 | Reporting: wording string in the JSON, tie count, hand check of the first 20 events of the biggest cell, plant_c and seed recorded | `wording`, `ties_d_zero`, `first20_events_biggest_cell`, `plant_c`, `seed` | |
| 23 | Only payloads from 2026-11-18T00:00Z (T_START) and before the end of the last complete UTC day; look number K = complete days from T_START to the end of the last hour file (read from file names esports_YYYYMMDDHH); K must be 1..20 else the run stops; K is not an option | `T_START`, `K = int((max(hrs) - T_START) // 86400)`, `t_hi`, `payloads_outside_look_window`, `SystemExit` | |
| 24 | Boundary z_K = C_OBF / sqrt(K/LOOKS), C_OBF 2.39, LOOKS 20 (simulated type I error 0.0122 one-sided per primary cell) | `C_OBF`, `LOOKS`, `zb` | |
| 25 | z = md / SE, SE = sd of the match-clustered bootstrap of the cell mean (5000 draws); 'meets bar at look K' = z >= zb and mean d >= 0.005 and share >= 55 and 12 matches and 60 events; 'PM moved first' = z <= -zb | `boot` (returns ci, se), `zstat`, verdict block | |
| 26 | Power check at this look: zb x SE < 0.01 (and share of d - md + 0.01 > 0 >= 55%); else 'unknown (underpowered at look K)'; 'no lead detected' only if it passed | `plant_ok`, `min_detectable_effect_at_this_look` | |
| 27 | Daily outputs: matches_by_day, matches_cumulative_by_day, plain_summary, look, boundary_z, data_through_utc | cell dict, `res["plain_summary"]`, `res` header | |
| 18 | Result carries clock note (required argument), bm values, drops, match list | `--clock-note`, `audit.bm_values`, `drops`, `match_list` | |

Author's own weak points, please test hardest: (a) rows 11 and 14 (windows of 60 s cannot resolve a lead under about 5 s); (b) row 6 relies on the stored payload sequence: if capture.py stores only changed polls, a market absent for one payload clears the baseline; (c) row 8 assumes map-N alignment; (d) `rnd` is shared between cap sampling, placebo draws and bootstrap, so results depend on iteration order (deterministic for fixed files).
