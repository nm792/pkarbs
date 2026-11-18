# AMENDMENT to feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md (18 Nov 2026, before any scored data is read; checker's questions)

1. Boundary direction: "z_eq x sqrt(t) >= 2.60" means z_eq >= 2.60 / sqrt(t) (a falling boundary), as in Goalserve PREREG V17. Any other reading in the PREREG or in the daily note is wrong.
2. Primary series: ONE. H1 is scored on round-win events against the Map N Winner market ("map" series) only. The Match Winner ("match") series is informational, no alpha, never relayed as a pass.
3. Wrapper note (checker, 18 Nov): feeds/ps_lead_test_cs2_latency.py has seven patch strings, not six; each target occurs once; tonight's output is EXPLORATORY and UNCHECKED.
4. Checking: the checker thread writes the daily-look script; the PandaScore thread checks that code against the PREREG and signs the second line of the rule-to-code table.
