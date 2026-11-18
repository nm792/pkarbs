# SIGNED: Goalserve feeds to IT, 18 Nov 2026 07:25Z

1. **Goal:** daily Goalserve odds looks from 19 Nov ~01:00Z.
2. **Measured position:** the checker thread signed **d3a8849a** (PR #409, row 32 `--smoke`); addendum at the end of reviews/SIGNOFF-goalserve-odds-vs-pm-v2-sequential-REVISED-2026-11-18.md. It supersedes my SIGNED note for 9d4857d4 as the commit to run.
3. **Most important item:** run P18 as chunk E1b (the only chunk that contains `--smoke`) and post exit codes before 10:00Z. Chunk F (P21) must NEVER contain `--smoke`; every daily JSON must show `smoke_not_a_result` false, the right `look` and `data_through_utc`. Run F from the clean export (my 06:10Z ruling) at or after d3a8849a.
