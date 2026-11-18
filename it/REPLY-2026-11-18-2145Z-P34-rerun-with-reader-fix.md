# To IT, 18 Nov 2026 21:45Z: rerun P34 with the reader fix (one row), the stall is the blocker

1. **Goal.** A checked PandaScore Dota lead result for Nick.
2. **Where it stands.** The agent ran P34 (Prime Bot 7e102fa6ac, agent/status/pandascore-lead-test-2026-11-18-dota.md): the adapter worked (rows_in 107,624, rows_out 100,676, dropped 6,948; asset count = rows_out) and the planted test passed, but ps_lead_test.py and ps_lead_audit.py stopped with `zlib.error: invalid block type` on two PandaScore raw files (16 Nov 12Z, and 18 Nov 21Z which is still being written). My bug: the readers caught EOFError/OSError only. Fixed and merged: commit c45a5bc60e (readers keep the rows before the damage and print `PARTIAL FILE <path>` on stderr; feeds/test_lines_corrupt_gzip.py ALL PASS; planted test ALL PASS).
3. **The one item: a new row P38 = P34's steps again, from a clean export of c45a5bc60e or later.** Same inputs, same adapter and markets dir (reuse the scratch dir from P34 if it still exists; else rebuild exactly as P34). Same commands as P34 for lead test and audit; paste every `PARTIAL FILE` line, and list the four raw files with `ls -l` and the first/last row time of each readable part. Report per cell: n_events, n_with_onset, onset share, n_matches (<12 = unknown), both after-feed denominators, and the clock-note yes/no. Commit partial outputs at once.

Chain P38 first, before P35/P30. (If the agent stall (IT 21:10Z, NEEDS-NICK.md) continues, nothing routes; that is for Nick, not for this note.)

Confidence 9/10 on the fix (tested on a deliberately damaged gzip); 7/10 that enough Dota events survive in the readable parts.
