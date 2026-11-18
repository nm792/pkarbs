# To IT, 18 Nov 2026 ~18:30Z: URGENT, PandaScore Dota lead test on ALL stored data since 13 Nov (result due 19:45Z)

1. **Goal.** A Dota lead result for PandaScore's low-latency WebSocket, per feeds/STANDARD-feed-latency-test.md v1, measured against each Polymarket token's own book. Nick (18 Nov 18:16Z): we have had these feeds for days; do not wait for BLAST.
2. **Measured position.** The 16 Nov rerun (agent/status/pandascore-lead-test-2026-11-16.json, 23 matches, 1,911 events) is UNCHECKED, and its Dota cells are not usable until the rule-to-code table is signed. The script is feeds/ps_lead_test.py; the checker thread is "Audit CS2 model".
3. **Most important item.** One run over all stored PandaScore data from 13 Nov to now, with PM books for every Dota market that matches.

## P-A (read-only, ~18:45Z): inventory, one reply
- PandaScore files: `/mnt/HC_Volume_107257520/pkarbs/pandascore/raw/` first and last file name, count, GB; any missing hours (list them); Dota match ids seen.
- PM store(s): every dir holding markets + books or trades for the Dota markets 13 Nov to now (e.g. `share/books.jsonl.gz`, the 16-17 Nov capture `/vol2/pkarbs/dotacap/run-2026-11-16/out/books.jsonl`, the trade recorder since 14 Nov 02:09Z). For each: date range, and **whether it holds the YES token, the NO token, or both, as separate books**. State plainly which Dota markets have each token's own book. A YES-only store gives no result for the NO side; do not derive NO from YES.
- Free space on the data volume now.

## P-B (run after P-A, one process, memory cap)
`python3 -I feeds/ps_lead_test.py --ps /mnt/HC_Volume_107257520/pkarbs/pandascore/raw --pm <DIR1> [--pm <DIR2> ...] --out agent/status/pandascore-lead-test-2026-11-18-dota.json` from a clean export of origin/claude/project-thread-vg2ckg (as for Goalserve). Push the small JSON and a stdout/stderr log only. Then run feeds/ps_lead_audit.py on the same inputs as the checker's inputs. Report Dota cells (n events, n matches, onset %, median real vs placebo, CI, price-after-feed %) and the verdict line.

## What I do meanwhile (by 19:15Z)
Draft the rule-to-code table for ps_lead_test.py (STANDARD v1 rows 2-3 against the code lines) and ask the independent checker thread to fill and sign it. Until it is signed, the result goes to Nick labelled UNCHECKED.

Deadlines: P-A reply by 18:50Z; P-B result by 19:45Z. If the PM stores do not hold each token's own book for Dota, say so in P-A at once; that changes what can be tested and Nick must hear it.

Confidence 8/10 that the inputs exist (paths from earlier IT and Hermes notes); P-A settles it.
