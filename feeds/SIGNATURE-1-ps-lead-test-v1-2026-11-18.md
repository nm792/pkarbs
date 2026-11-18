# Checker signature on RULE-TO-CODE-pandascore-lead-v1-2026-11-18.md (feeds/ps_lead_test.py), 18 Nov 2026 about 19:10Z

Independent re-read of feeds/ps_lead_test.py at 9bb454b6ec (no change to the script since 97dbca96) against STANDARD v1 s2-3. Author's table: Dota-feed thread. Checker: "Audit CS2 model" thread. Planted-case test written by the checker: feeds/test_ps_lead_planted.py (ALL PASS: cs2 and dota2, map series; PM +10 s after the feed gives median lead +9.94 s and 'meets bar'; PM 10 s before gives -10.04 s and 'no lead'; PM that never reacts to events does not pass).

**Verdict: SIGNED as CHECKED for the all-data Dota run, with the labels below. Every "meets bar" is still only "(needs audit)".**

Rows 1-2, 6, 8, 10-15, 17: confirmed OK by my own read. Differences:
- D1 (events not independent, two events in one message): CONFIRMED, limit. The match-clustered bootstrap covers dependence between events of a match; n >= 30 counts events. The script has NO minimum number of matches: report n_matches next to every cell and treat a cell with fewer than 12 matches as unknown whatever the CI says.
- D2 (clock): CONFIRMED. The script takes no clock note; the report must say whether the PandaScore capture and the Polymarket recorder run on the same host/chrony. Without it the lead has no stated resolution.
- D3 (no start-time check): CONFIRMED and worse than stated: `sel[(mid, kind)] = m` lets the LAST of several same-name markets win silently, and nothing counts how many matches had more than one candidate. Report the count of matches whose name pair has more than one market (IT can count it from markets.jsonl); those matches are suspect.
- D4 (game order from first-seen game_id): CONFIRMED. A series joined mid-way pairs events with the wrong Map N market. Report matches whose first message is not game 1 if the data show it; otherwise a known limit.
- D5 (one token missing): CONFIRMED.
- D5b: REFINED. Events with no book (or no mid at t-60 s) are counted in `n_events` and `pct_real_with_onset`, but `median_real_lead_s`, `diff_s`, the bootstrap and `pct_price_after_feed` use only events WITH an onset, so medians and the 60% share are not biased by them. What they inflate is the n >= 30 gate and they deflate the onset share. Required label: report `n_events`, `n_with_onset` and the onset share side by side; apply the n >= 30 gate to `n_with_onset`. For the all-data run this matters: the Dota PM books stopped 16 Nov 22:59:59Z, so every Dota event after that has no book.
- D6 (share denominator): CONFIRMED as stated: the script uses events with an onset; STANDARD bar 4 says "events" without a denominator, the PandaScore CS2 PREREG says "events with an onset". Report BOTH shares. If only the onset-based one reaches 60%, say so in the verdict line.
- New E1 (placebo draws): `plc` draws times over the whole match and a token from any game's market of that series, so a Map 2 time can use a settled Map 1 token that never moves. This lowers the placebo onset count (noise), it does not create a lead. Known limit; my CS2 daily script fixes it (D1 there).
- New E2: `diff_s` is the difference of POOLED medians (all real leads minus all placebo leads), not a median of paired differences, so matches with many events weigh more. STANDARD wording "median (real minus placebo)" is read that way; flag in the report.
- New E3: the percentile bootstrap resamples matches; with about 12-25 matches it under-covers (my simulations: 3-4% false pass per cell at one look). Four cells per title (map/match x strata) multiply that. So "meets bar" is a screening result and needs the audit; "no lead" is not affected.
- New E4: a message without `round_score`/`kills` in `available_fields` overwrites the baseline with an empty dict, so the next real rise is lost (missed events, no bias to a pass).

Planted-case test: exists now (feeds/test_ps_lead_planted.py, written by the checker). Run it before every real run: `python3 -I feeds/test_ps_lead_planted.py` must end with ALL PASS.
Confidence 8/10 that the rows and differences above are complete. Not yet run on real data.
