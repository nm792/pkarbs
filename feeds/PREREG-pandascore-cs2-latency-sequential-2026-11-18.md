# PRE-REGISTRATION: PandaScore CS2 new fields, sequential daily looks. Locked 18 Nov 2026 about 18:30Z (late: due 18:00Z). No scored data has been read.

Cites feeds/STANDARD-feed-latency-test.md v1. Deviation from STANDARD v1 section 3 bar 3 (CI replaced by the boundary below) approved by Nick on the decision card, 18 Nov 08:24:45Z. Benchmark is the Polymarket price (the target token's own book).
Sources: PandaScore docs fetched 18 Nov (feeds/PandaScore-low-latency-feed-counter-strike-2026-11-18.html, page updatedAt 2026-11-17T16:45:27Z).

## What the docs say (read, not guessed)
- New fields per player: hp, armor, primary_weapon, secondary_weapon, utility, has_bomb, has_defuse_kit, kills, deaths, current_money_balance, loadout_value; per team: current_money_balance, loadout_value, buy_phase_main_weapon_value; `previous_rounds` with outcome and winner_team_id.
- `latency`: list of {field, delay}, delay in ms RELATIVE to the fastest data point in that message. It is not an absolute delay: it says round_score vs player_* ordering, never round_score vs the real world. Sample: round_score 0, round_timer 0, bomb 0, side 0, rounds_summary 0, all player_* 13234 ms. Docs: "For CS2, the round score is usually the fastest."
- Updates are pushed on every state change, including a HP change.

## Sample
Only CS2 messages with receive time at or after 2026-11-19T00:00Z. Everything earlier is exploration and never scored.

## Hypotheses
- H1 (the only one that can pass; alpha spent on it alone): CS2 round-win events (home/away score counter rises between consecutive messages of one game, as in ps_lead_test.py) lead the PM price, in the stratum where round_score delay == 0 in the producing message (round score is the fastest point). The lat>0 and lat_unknown strata are reported, never scored.
- H2 (informational only, no alpha): events from player_alive true to false (needs `player_alive` in available_fields and the player-level delay reported). H3 (informational only): bomb status becomes planted (needs `bomb` in available_fields).
- Economy, weapons and HP are not events. They are reported as covariates only, in a later note.

## Statistic and boundary (Goalserve PREREG V17 shape)
Event, receive time (our recv_ns), onset (>= 2c in the event direction within -60 s/+60 s of receive time), placebo (10 random event-free times per match, same procedure): ps_lead_test.py rules unchanged. Per match: mean of (real lead minus mean placebo lead) over events with an onset in both. The cell statistic is the t-statistic of the per-match means (n-1 df) converted to z_eq. N_MAX = 60 matches, matches ordered by first usable event time, later data never changes earlier matches; information time t = matches / 60. Pass boundary z_eq x sqrt(t) >= 2.60 (reflection bound, one-sided alpha 0.0093, spent on H1 only). "PM moved first" at -2.60. A pass also needs, within the same stratum: median (real minus placebo) >= +2.0 s, price moves after the feed in >= 60% of events with an onset, n >= 30 events, >= 12 matches. A volume stratum (below / at or above $25k) is only reported if the volume map has a documented provenance; otherwise reported as "strata not computed". "no lead" is only said when 60 matches are reached or the last look is done, and the planted-edge check passed.

## Looks
One per complete UTC day, first look on 20 Nov (about 01:00Z) on 19 Nov data, last look 1 Dec (30 Nov data) or the day before the trial ends. A pass stands and is audited. Every look is UNCHECKED until another thread signs the rule-to-code table and hand-checks the first 20 events.

## What is not built yet (stated, not hidden)
The per-match t-statistic, the boundary and the daily planted-edge check are NOT implemented in ps_lead_test.py (it uses a pooled bootstrap CI). A daily-look script (same shape as feeds/goalserve_odds_vs_pm_v2.py) and its rule-to-code table, written or checked by a thread other than the author, are needed before look 1 counts. Due 19 Nov 18:00Z. If late, look 1 is run with the unchanged ps_lead_test.py, labelled "exploratory, no pass possible".
