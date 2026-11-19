# RULE-TO-CODE table: feeds/ps_lead_test.py (PandaScore low-latency WS vs Polymarket price), 18 Nov 2026

Rules: feeds/STANDARD-feed-latency-test.md v1 sections 2-3 (cited, not restated) and the docstring of feeds/ps_lead_test.py. Code read at origin/claude/project-thread-vg2ckg (script blob as of commit dbc22c11da). **Filled by the Dota-feed thread (author of the run request), NOT independent. Status: UNSIGNED. The independent checker thread ("Audit CS2 model") must re-read the code, fill the right-hand column itself, and sign. Until signed, every number from this script is UNCHECKED.**

| # | Rule (STANDARD v1) | Code (function, behaviour) | Difference found |
|---|---|---|---|
| 1 | Event = state change diffed from consecutive messages of the same game | `load_ps`: per (match_id, game_id), counter increase vs previous message; hello clears baseline; first message only sets baseline | OK. Dota fields: kills, towers, barracks, roshans per side, only if in `available_fields`. |
| 2 | Event types named before data | `counters`: Dota kills/towers/barracks/roshans; CS2 round score | OK, matches the PandaScore task (13 Nov). |
| 3 | One event per real change | One row per counter that rose | **D1: a message where kills and towers both rise gives two events at the same instant, and one kill burst gives many events. n is inflated and events are not independent. Match-clustered bootstrap partly covers it; n>=30 does not.** |
| 4 | Receive time on ONE shared clock with the price rows | PandaScore `recv_ns`; PM `recv_ms`/`ms` from books rows | **D2: not checked in code. The two captures are separate processes, maybe separate hosts. The run needs a clock note (same chrony host yes/no).** |
| 5 | Match market by team names plus start time | `mk_index`/`sel`: exact normalised set of two outcome names; no start-time check | **D3: no start-time check; a repeat pairing the same day would merge.** |
| 6 | Side by settlement, not co-movement | Direction = scoring team's own outcome token must rise >=2c | OK for direction. No settlement check needed for the direction rule. |
| 7 | Map market for game N | `gorder`: order of first-seen game_id per match; market 'Map/Game N Winner' | **D4: if the capture joined mid-series, or a game_id was first seen late, game order shifts and events pair with the wrong game's market.** |
| 8 | Price = each token's own book | `books` reads rows by `asset`/`tk` token; mid = (best bid + best ask)/2 of that token's own book; only needed tokens | OK (no NO=1-YES). **D5: if a store holds only tokens[0] of a market, events for the other team find no series.** |
| 9 | Events with no usable price | `onset` returns None when no book rows; row still counted in n and in 'pct_real_with_onset' | **D5b: events whose token has no book are counted as "no onset" instead of being excluded. They deflate n_with_onset and bias price-after-feed. Must be excluded or reported separately.** |
| 10 | Onset: first mid move >=2c in event direction in [-60,+60 s] | `onset`: base = mid at t0-60 s; first book row up to t0+60 s with sign*(mid-base) >= 0.02; returns time - t0 | OK. Resolution: book snapshots are late by ~0.1-2 s (STANDARD says state it). |
| 11 | Lead = onset - receive time | same | OK. |
| 12 | Placebo: 10 random event-free times in same match, same procedure | `plc`: 10 per (match, series), uniform within the match's event span, no event within 60 s, random token among that match's tokens, random sign | OK. Note: placebo token chosen from tokens that had events; seed fixed 20261115. |
| 13 | n>=30 per title (and per stratum if reported) | cell n < 30 -> "unknown" | OK. Strata only with `--vol`; without it only 'all' is computed. |
| 14 | Median(real - placebo) >= +2 s | `diff_s` = med(real leads) - med(placebo leads) | OK. Medians over events with onset only (see #9). |
| 15 | Bootstrap CI by match excludes 0 | `boot`: resample matches, 2000 draws, 2.5/97.5% | OK. Placebos resampled with the same matches. |
| 16 | Price moves after the feed in >=60% of events | `pct_price_after_feed` = share of events WITH onset where lead>0 | **D6: denominator is events with onset, not all events. Report both.** |
| 17 | Verdict wording | 'meets bar (needs audit)' / 'no lead (needs audit)' / 'unknown' | OK; never a pass before the audit (STANDARD s4). |

## Planted-case check (needs doing, runs before the real run)
A synthetic PandaScore file and a synthetic book where (a) the price moves 10 s after the message must give lead ~ +10 s and meet the bar at n>=30; (b) the price moves 10 s before must give lead ~ -10 s and fail; (c) no price move gives onset None for events and placebos and must not pass. Tests: feeds/test_ps_lead_* if present; otherwise this must be written by the checker.

## Run conditions requested for the all-data Dota run
Fix D5b and D6 (report both denominators) or label them in the output; state D2 clock note; D1, D3, D4 reported as known limits with a count of affected events where the script can count them. Nothing here changes the STANDARD thresholds.
