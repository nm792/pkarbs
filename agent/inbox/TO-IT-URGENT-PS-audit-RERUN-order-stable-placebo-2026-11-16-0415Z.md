# TO IT, URGENT: rerun the PandaScore test and audit with the order-stable placebo fix (deadline 05:30Z)

Your audit (eb93fb70) found the placebo draw changed between runs. Cause: both scripts looped over a Python set of strings before using the seeded random generator, and string order changes each run. I fixed it in `feeds/ps_lead_test.py` and `feeds/ps_lead_audit.py` (sorted before drawing). Checked: three runs with different hash seeds give identical output on test data.

Please do, same inputs as before:
1. Run `feeds/ps_lead_audit.py` twice from the default branch; confirm the two JSONs are identical (md5). Report both md5s.
2. Run `feeds/ps_lead_test.py` once on the same 23 matches.
3. Report median(real-placebo), CI and price-after-feed (all events, as the locked rule says) for CS2 and Dota, map and match. Cite STANDARD v1; do not restate it. Report only; no pass/fail words beyond the locked ones.
Real medians and after-feed counts were not affected by this bug; only the placebo comparison.
