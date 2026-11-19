# URGENT to IT: run the PandaScore CS2/Dota lead test (script ready, deadline 15 Nov 07:30Z, computed results only)

From: the results thread. 15 Nov 2026, 05:40Z. Nick: data has been captured since 13 Nov and there are no results. Cites `feeds/STANDARD-feed-latency-test.md` v1 and Part B of `agent/tasks/TASK-pandascore-trial-2026-11-12.md` (events, strata and bar are already pre-registered there; nothing is changed). Read-only analysis, Type A, no unit or collector change, one process, memory cap and timeout as in agent/PROTOCOL.md.

## Run
`feeds/ps_lead_test.py` (committed with this note). Tested on synthetic data with hand-known leads (feed first by 5 s, price first by 20 s): it returns the right sign both times.

    python3 feeds/ps_lead_test.py --ps /mnt/HC_Volume_107257520/pkarbs/pandascore/raw \
        --pm <dir with markets.jsonl + books.jsonl, esports PM capture since 13 Nov 17:06Z> [--pm <more dirs>] \
        --out /mnt/HC_Volume_107257520/pkarbs/scratch/ps_lead_20261115.json

Use the PM capture dirs that hold the 345 registered esports matches (the 14 Nov 13:25Z recount's `polymarket` block); you know which. Include the 15:00Z/13:00Z append-streamed hours (the script's reader stops quietly at a truncated gzip tail).

## Before you report (setup check, Nick's rule)
1. Print for 3 matches: PandaScore team names, the PM market title/outcomes it matched to, and 3 events with recv time and the PM mid before/after. Names are matched EXACTLY after normalisation, so unmatched matches are counted (`ps_matches_unmatched_to_pm`), not guessed.
2. Confirm PS rows and PM book rows are on the same host clock (recv_ns vs recv_ms). State resolution (book rows are late by about 0.1-2 s).
3. If a count differs from the 14 Nov recount (CS2 702 round changes, Dota 1,069 kills, 243 towers, 76 barracks, 38 Roshans) by more than 5%, say why before anything else.

## Report (commit `agent/outbox/ps-lead-test-2026-11-15.md` plus the JSON under agent/status/)
Paste the `cells` table as is: per title (cs2, dota2), per series (map / match), per stratum (all, <25k, >=25k): n events, n matches, % with price onset real vs placebo, median real and placebo lead, difference, 95% CI (match bootstrap), % price after feed, verdict word. Under 30 events = 'unknown', never pass or fail. Label numbers 'sim on real data'. No pass/fail claim goes to Nick before the independent audit (STANDARD section 4); say so in the report.

## Deadline
Report by 07:30Z (dispatch idle since 16:37Z 14 Nov; if no session can run this, IT says so in the reply and the coordinator tells Nick). This goes ahead of the LoL S0 (09:00Z), which is a count/coverage check.
