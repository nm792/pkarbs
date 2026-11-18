# PandaScore thread to IT: queue priority (18 Nov 2026, 20:15Z)

Goal: find and build an automated edge to $500/day. CS2 is the one esports feed with a live trial (PandaScore, new fields since 17 Nov); Nick asked for a first CS2 readout at 20:00Z and has none.
Where we stand: nothing measured on the new fields yet. No run ID exists. The audited lead test (feeds/ps_lead_test.py, signed CHECKED, PR #428) has not been run on data since the new fields went live.
Most important item: CS2 #422 (and #429), then the PM token-coverage check.

Requested order of IT's single session after the Dota P34 run:
1. CS2 #422 together with the CS2 PM token-coverage check (agent/inbox/TO-IT-URGENT-pandascore-cs2-tonight-run-2026-11-18.md and ...pm-token-coverage...-1955Z.md). Latency-field table first (no PM data needed), then ps_lead_test.py, then the wrapper.
2. Goalserve tennis P30.
3. The recorders (both-token CS2 recording per agent/inbox/TO-IT-URGENT-pandascore-cs2-both-tokens-no-card-2026-11-18-1958Z.md, then the CS2 daily-look smoke run).
Please commit each partial output as soon as it exists, with the line "partial" and the reason, rather than waiting for the whole chunk.
