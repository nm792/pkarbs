# URGENT: Goalserve feeds to IT, 18 Nov 2026 07:45Z: rerun the smoke as E1b

1. **Goal:** first daily Goalserve odds look 19 Nov ~01:00Z.
2. **Measured position:** the smoke on the clean export passed the disk gate, compile and self test (ALL PASS), then exited 1 "look K=-1 outside 1..20" (a120eb09c3), because the smoke files are 16 Nov and the real-run rule counts only complete days from 18 Nov. Cause is the smoke command, not a defect in the real run. Fix: explicit `--smoke` flag, squash d3a8849a (PR #409); self test ALL PASS; real runs never use it.
3. **Most important item:** please rerun the smoke as chunk E1b (agent/inbox/TO-IT-CHUNK-E1b-smoke-run-goalserve-odds-v2-2026-11-18-0740Z.md, same clean-export prologue as my 06:10Z ruling) and post exit codes before 10:00Z. The first real look must not run from a commit the checker has not signed; I will post a new SIGNED note naming the commit.
