# URGENT, LATE: PandaScore CS2 tonight run (18 Nov 2026, 19:43Z)

agent/inbox/TO-IT-URGENT-pandascore-cs2-tonight-run-2026-11-18.md (issue #422, due 19:40Z) has no answer in agent/outbox or agent/status at 19:43Z. The last Prime Bot commits are the heartbeat (19:00Z) and P33, the Dota inventory (19:30Z), which is not this task. Nick asked for a CS2 readout at 20:00Z.

Please do now, in this order, and commit each part as soon as it exists (partial is fine, say "partial" and why):
1. Step 1 and step 4 of the original note (first message with a `latency` key; per-field delay table). They need no PM data.
2. Step 3a: `python3 feeds/ps_lead_test.py` (now signed CHECKED by the checker, PR #428) on the symlinked hours.
3. Step 3b: `python3 feeds/ps_lead_test_cs2_latency.py` on the same inputs.
Then the smoke run in agent/inbox/TO-IT-pandascore-cs2-smoke-2026-11-18.md.
Reports from ps_lead_test.py must show n_events, n_with_onset and onset share side by side, both price-after-feed denominators, n_matches per cell, the clock note, and the number of matches with more than one PM market for the same names (checker's rule, PR #428).
If something blocks you (disk, time, a refusal message), commit the exact message and stop. Do not edit scripts.
