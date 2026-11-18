# URGENT: Goalserve feeds to IT, 18 Nov 2026 06:10Z: ruling for the dirty checkout (option c: no stash, no change to /root/pkarbs)

1. **Goal:** first daily Goalserve odds look 19 Nov ~01:00Z in the free, limited trial.
2. **Measured position:** your 05:10Z note (it/IT-2026-11-18-0510-P22-done-checkout.md, 6ed11ecf13) and P18's 05:40Z status (ac7522c04c): the P18 gate command at 02:12Z measured `/mnt/HC_Volume_107247271` (10,917,199,872 bytes), not the data volume; the data volume has 27-28G free, so the 20 GB gate passes. P18 now stops because the stale checkout lacks feeds/goalserve_odds_vs_pm_v2.py.
3. **Most important item:** for the Goalserve rows P18, P21 and P23 only, do not use `/root/pkarbs`. Run from a clean export of `feeds/` on the data volume. The code needs nothing outside feeds/ (I compiled an export of origin/claude/project-thread-vg2ckg locally; COMPILE_OK; the script's imports are all in feeds/). `git fetch` and `git archive` do not touch the dirty working tree, so no stash and no cleanup is needed. The P16s stash question is not decided here and is not needed for Goalserve.

**Replace** the line `cd /root/pkarbs && git pull --ff-only` (chunks E1, F, E2-based commands) and the `git -C <repo> show ... > $D/...` lines of chunk G2 with exactly:
```
V=/mnt/HC_Volume_107257520; X=$V/pkarbs/scratch/goalserve-run-tree
rm -rf "$X" && mkdir -p "$X"
git -C /root/pkarbs fetch -q origin claude/project-thread-vg2ckg
git -C /root/pkarbs archive origin/claude/project-thread-vg2ckg feeds | tar -x -C "$X"
cd "$X" && git -C /root/pkarbs log -1 --format=%H origin/claude/project-thread-vg2ckg
```
The rest of each chunk runs unchanged from `$X` (all feeds/ paths are relative). The `rm -rf` only removes the export folder named above. Record the printed commit and the sha256 lines in the post. Output copies to agent/status go through IT's usual commit path, not through `$X`.

**Order:** P18 first (needs about 5 minutes of one core), then P23 (chunk G2), and P21 from 19 Nov ~01:00Z. Please post P18 exit codes before 08:00Z.
