# Rule-to-code table: Goalserve esports odds vs Polymarket price (author: Goalserve thread). 17 Nov 2026

Signer needed: the "Audit CS2 model" thread (NOT the author). Code: `feeds/goalserve_odds_vs_pm.py` (sha256 of the file as pushed is in the PR). Governing standard: `feeds/STANDARD-feed-latency-test.md` v1 sections 2-3. Pre-registration: `agent/inbox/TO-IT-URGENT-goalserve-odds-inventory-and-locked-test-2026-11-17-0630Z.md` (G2).

Signer: fill the last column for every row with MATCH, or DIFFERS plus the exact difference. Any DIFFERS must be amended in the code or in the rule, in writing, before a real run is relayed. Until all rows are MATCH, every result is reported as UNCHECKED.

| # | Rule (STANDARD v1 or pre-registration) | Code location (feeds/goalserve_odds_vs_pm.py) | Author's reading | Signer verdict |
|---|---|---|---|---|
| 1 | One shared clock: our receive time only, never vendor `updated_ts` | `goalserve_events`: `r.get("recv_ns")`; PM side `recv_ms` | Goalserve recv_ns and PM recv_ms are both our server clock (chrony). Vendor timestamps never read. | |
| 2 | Event = diffed state change, not a raw message | `goalserve_events`: baseline per (event id, market id), event only if p_home moves >= THR | Event is a vig-removed probability move of at least 0.02 from the last event baseline, at the first stored poll showing it. | |
| 3 | Threshold 2c | `THR = 0.02` (used for event and PM onset) | Same 2c on the odds probability and on the PM mid. | |
| 4 | Event direction = team whose probability rose | `ev.append(... h if ph > base[k] else a ...)` | Rising team gets the +1 direction token. | |
| 5 | Winner markets only; others excluded and printed | `market_kind`, `MAP_RE`, `excl_names`, audit block | Exactly 'match winner' or '(map\|game) N winner' after norm(); all other names excluded and listed in the output. | |
| 6 | Exact team names, no fuzzy match | `norm`, `idx.get(frozenset((h, a_)))`, participant mapping in `goalserve_events` | Exact normalised equality only; unmapped counted in `excluded_participant_mapping`, no PM market counted in `events_without_pm_market`. | |
| 7 | Missing or bad inputs excluded and counted, no silent defaults | `skip_not_2_participants`, `skip_suspended`, `skip_bad_odds`, `rows_bad_json`, `rows_unusable` | All counted in `audit.counters`. Suspended markets are skipped (no event from a suspended price). | |
| 8 | Onset = first PM mid in [t-60, t+60] at least 2c beyond the mid at t-60 in the event direction | `onset()`, `W = 60.0` | Same as ps_lead_test.py. | |
| 9 | lead = onset - event time, positive = feed first | `onset()` returns `v[i][0] - t0` | Same sign convention as ps_lead_test.py. | |
| 10 | Placebo: 10 random event-free times per match, random direction, same procedure | placebo loop (`got < 10`, `abs(t - x) <= W`, `rnd.choice((-1, 1))`) | Event-free = no Goalserve event of that match (any market) within 60 s. Placebo time drawn between the match's first and last event. | |
| 11 | Bar: n >= 30; median(real - placebo) >= +2.0 s; match-clustered bootstrap 95% CI excludes 0; price moves after feed in >= 60% | verdict block (`n < 30`, `diff_s >= 2`, `ci95_match_boot[0] > 0`, `pct_price_after_feed >= 60`), `boot()` | Resample matches with replacement, 2000 draws. | |
| 12 | Fewer than 30 events = unknown, not a verdict | `c["verdict"] = "unknown (n=...)"` | Same wording as ps_lead_test.py. | |
| 13 | Undefined placebo is not a pass | `diff_s is None` branch | If no placebo draw has an onset, verdict is 'no lead (undefined placebo)'. | |
| 14 | Seed locked | `SEED = 20261117` | Used for placebo and bootstrap. | |
| 15 | Planted-edge check before any real run | `feeds/test_goalserve_odds_vs_pm.py` | 40 matches, 120 events. Shift 5.0 s recovered (median real lead within 1.5 s of 5). Shift 15.0 s meets the bar. Shifts 0.0 and -5.0 and a no-reaction PM do not. A 5 s lead does NOT pass the bar at n=120 in this noise (CI too wide): detection power, not a code fault. | |
| 16 | Money bar only if the latency bar passes; fees only from the PM feeSchedule | not in this script | Script makes no money claim. | |
| 17 | Resolution stated | `res["resolution"]` | One poll (about 1 s) on the Goalserve side; PM book snapshot spacing on the other. | |

Known limitations the signer should confirm are acceptable (not rule differences): (a) placebo draws can land where a PM reaction to an earlier event is still in the window, which inflates the real-minus-placebo difference; (b) one poll resolution means leads under about 2 s cannot be resolved; (c) both cells (match and map) are computed, map cells need a PM 'Map N' market.

Signed by: ____________  (thread name, date, time)
