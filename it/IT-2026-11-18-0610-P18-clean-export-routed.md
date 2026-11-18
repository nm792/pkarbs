# IT note to PK arbs, 18 Nov 2026 06:10Z: P18 reopened on the clean export; P23 and P21 follow

1. **Goal:** first daily Goalserve odds look 19 Nov ~01:00Z in the free trial.
2. **Measured position:** P18 ran at 05:42Z and stopped at its file check: the local checkout HEAD 026be71f lacks both v2 files (agent/status/goalserve.md "## E1 smoke (18 Nov 05:40Z)", pkarbs ac7522c04c). The same post confirms the 02:12Z gate read `/mnt/HC_Volume_107247271`, the other mount; the data volume gate passes (29.4 GB free 05:30Z, dialogue status/DISK.tsv).
3. **Most important item:** your 06:10Z ruling (it/REPLY-2026-11-18-URGENT-goalserve-ruling-clean-tree-no-stash.md, 0d86452) is routed as written. P18 is the top `open` row; P18 exit codes are due before 08:00Z.

## Routed (dialogue OPEN.md, IT check 06:10Z)
- **P18 `open`:** the chunk's `cd /root/pkarbs && git pull --ff-only` line is replaced by your five-line export block exactly; the rest runs unchanged from `$X`; the commit and sha256 lines are to be recorded.
- **P23 `waiting: after P18`:** the same export block, then G2's df line and `nice -n 19 timeout 1800 python3 -I feeds/pm_recorder_inventory.py $V` from `$X` (replaces the `git show` line). Same session if it fits rule 2.
- **P21 `waiting`:** from 19 Nov ~01:00Z, after P18 ALL PASS, from the same export; never `git pull` in /root/pkarbs.
- Checked: goalserve_odds_vs_pm_v2.py inserts its own folder into sys.path, so `python3 -I` run from `$X` still finds ps_lead_test and goalserve_odds_vs_pm.

## Still yours
- P16 (shadow logger) still waits on the P16s stash ruling (1.98 GB untracked, pkarbs 81d3ad3f).
- P17a waits on the capture output folder and config path, or a decision to drop Part A.
- P4 waits on a ruling on the NVDA perp partial (6cd69906).
