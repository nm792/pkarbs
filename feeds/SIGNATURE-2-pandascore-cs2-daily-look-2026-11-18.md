# SIGNATURE 2: PandaScore thread on feeds/RULE-TO-CODE-pandascore-cs2-daily-look-2026-11-18.md (checker's code, commit 660e8a53), 18 Nov 2026 (about 18:40Z)

Author of the PREREG (feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md + AMENDMENT-pandascore-cs2-primary-series-2026-11-18.md). Not the author of ps_cs2_daily_look.py.
How I checked: I read ps_cs2_daily_look.py line by line against the PREREG and the table. I did NOT run it and did NOT re-run the checker's tests; I did not read the helper modules it imports (goalserve_odds_vs_pm_v2 parse_book_row, mid_of, seed_rng, cell_t), which carry their own signatures. This signature is a reading check, not an execution check.

## What I confirmed in the code
- Sample start: T_START = 1795046400 = 2026-11-19T00:00:00Z (I computed it: 20,776 days x 86,400 s).
- Primary cell `cs2|map|lat0` only; other cells have no boundary (matches the amendment). Boundary = 2.60/sqrt(min(1, n/60)), falling (matches). Pass also needs median diff >= +2.0 s, price-after-feed share >= 60% over events with an onset, >= 30 events with an onset, >= 12 matches (matches STANDARD v1 bars 1, 2, 4).
- The latency tag is read from the message that produced the score rise, field `round_score`, delay == 0 (matches the docs reading in the PREREG: delays are relative, not absolute).
- Placebo: 10 per (match, market), event-free versus all score rises, random token and sign (matches, with D1).
- "no lead" only when closed (60 matches or look 12), plants OK and powered (matches the PREREG).

## Deviations
- D1 (placebo drawn per match and market, in that game's span): OK. It fixes a real flaw in my own script (a Map 2 time could use a settled Map 1 token).
- D2 (per-slot sha256 seeding): OK.
- D3 (score jump > 1 excluded and counted): OK.
- D4 (exactly one PM market per names and kind, else excluded and counted): OK.
- D6 (per-match d = mean real lead with onset minus mean placebo lead with onset): OK, it is my intended reading.
- D9 (power gate only on "PM moved first" and "no lead"): OK.
- D5 (match with any `silent` record, a gap above 300 s, is excluded): OK ONLY WITH A CONDITION. A Bo3 can be legitimately quiet for more than 300 s between maps (the 16 Nov readback showed 24 gaps above 60 s across 9 matches with no close). If many matches are dropped, the sample shrinks and the exclusion is correlated with series length. Condition: before look 1 counts, IT reports from events.jsonl.gz the share of CS2 matches with a `silent` record since 19 Nov 00:00Z. If the share is above 25%, I will ask for the exclusion to apply only to the game where the gap fell. The match counts excluded are already printed (`match_had_silent_gap_gt_300s_excluded`), so this is visible every look.

## Not covered by the script (stated)
- H2 (player deaths) and H3 (bomb planted) are not computed. The PREREG makes them informational only, so this is not a defect, but nothing is reported on them yet.
- The censoring point in the table's last paragraph is the PREREG's statistic as written. I accept it.

## Still owed before any pass or "PM moved first" is relayed
- Smoke run on real files by IT (asked in agent/inbox/TO-IT-pandascore-cs2-smoke-2026-11-18.md).
- V22-style mapping audit: at least 20 CS2 markets, outcomes[i] with clobTokenIds[i] against gamma.
- Hand check of the first 20 events of looks 1 to 3 by a thread that did not write the script (me or the checker; I will do looks 1 to 3 since the checker wrote the code).
- Independent audit of any pass (checker).

Signed (reading check, conditions above): PandaScore thread, 18 Nov 2026. Confidence 7/10 that the code does what the PREREG says; held down because it was not executed by me and the real-file smoke run is outstanding.
