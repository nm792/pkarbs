# URGENT to IT: independent audit of the PandaScore lead test (locked rule, report by 16 Nov 04:00Z)

From: the results thread, 16 Nov 2026, 02:15Z, on the coordinator's instruction. Cites `feeds/STANDARD-feed-latency-test.md` v1 section 4. This file is the pre-registration: committed BEFORE the audit reads any data; do not edit it. The result under audit is `agent/outbox/ps-lead-test-2026-11-15.md` (16 Nov 01:33Z, 23 PS matches, 18 joined to PM).

Independence: the audit must be run by a session that did NOT run `ps_lead_test.py` on 16 Nov 01:33Z (the temperature or MFW sessions are fine; say which session ran it). The audit script `feeds/ps_lead_audit.py` is separate code (it does not import the test runner) but was written by the same thread that wrote the runner, so the auditor also reads it and records any disagreement with the STANDARD in the report. Tested on synthetic data in the live schema only.

## Run (one read-only process, same data as the test)
    python3 feeds/ps_lead_audit.py --ps /vol2/pkarbs/scratch/p318-recount/pandascore \
        --pm /vol2/pkarbs/scratch/ps-lead-20261115/pm [--vol <the same archived volume file the test used>] \
        --recount agent/status/p318-recount-2026-11-14.json --out /vol2/pkarbs/scratch/ps-lead-20261115/audit-20261116.json

## Locked checks and decision words (set now, before data)
A. Isolated events (the Dota question). Keep an event only if no other PS event of the same match lies within +-60 s of it. Same onset, lead, placebo (seed 20261116) as STANDARD section 2. Also % price-after-feed by nearest-event gap (<10, 10-30, 30-60, >=60 s).
   - Per title/series: 'no lead reproduced' if on isolated events % price-after-feed < 60 AND median(real - placebo) < +2.0 s; 'not confirmed as no-lead' if either threshold is met; 'unknown' if isolated n < 30. Report the all-event cell next to it.
   - Dota specifically: if isolated n < 30, say so and say what n would settle it (more matches), do not extrapolate.
B. Count reconciliation. Recompute increases and any-change per type per match for the 23 matches in --ps. State: (i) the totals; (ii) the recount's totals restricted to the same 23 match ids (the script prints them); (iii) which of the 26 recount match ids are missing from --ps (expected: 3). 'Explained' only if the recount restricted to the same 23 ids is within 2% of the any-change totals (CS2) / increase totals (Dota) in every type; otherwise 'unexplained', with the largest per-match gaps.
C. The five unmatched names (Apogee Esports vs Leo Team; BAKS Esports vs EX-Zero Tenacity; Hype Tech vs Phantom; Inner Circle x Insanity vs Nemiga Gaming; PARIVISION vs Yellow Submarine). Report for each: PS events, whether any PM market exists for that pairing (the script lists markets sharing a name token), and the kind of mismatch (spelling, sponsor tag, 'x'/'vs' text). Do NOT add them to any result by fuzzy matching. If a market obviously exists under a different spelling, say so; any addition needs Nick's approval as a deviation from STANDARD v1.

## Report
`agent/outbox/ps-lead-audit-2026-11-16.md` + the JSON under agent/status/. Paste the A cells, the gap-bucket table, B and C as calculated. Label 'sim on real data'. No pass/fail beyond the words above. Say what was NOT checked (e.g. the volume file's source). Deadline 04:00Z; partial with n shown if unfinished. This goes ahead of MFW and temperature rows (Nick's request via the coordinator).
