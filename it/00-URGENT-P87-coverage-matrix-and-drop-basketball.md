# 00-URGENT to IT, 20 Nov 2026 04:05Z (Goalserve thread; Nick 03:18Z: "you cannot even record matching books?"). Read-only items 1-2 first; item 3 is a restart.

1. **Goal:** measure, per feed, whether a matching Polymarket book exists for the same matches (token match rate, last 24 h). Read-only, writes `scratch/goalserve-desc/coverage.json`. Table that it fills: `reviewer/FEED-RECORDER-MATRIX-2026-11-20.md`.
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/scratch/goalserve-desc; mkdir -p $D
git -C /root/pkarbs fetch -q origin reviewer; for f in coverage_matrix.py test_coverage_matrix.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $D/$f; done
export FEEDS_DIR=$V/pkarbs/scratch/goalserve-run-tree/feeds
python3 -I $D/test_coverage_matrix.py | tail -2      # must end ALL PASS
G=$V/pkarbs/goalserve; P=$V/pkarbs
nice -n 10 ionice -c3 timeout 2400 python3 -I $D/coverage_matrix.py --pm-dir final=$P/thesports/final-topics-32295b --pm-dir pmcs2=$P/pmcs2 --pm-dir pmdota=$P/pmdota --gs-dir esports=$G/esports_payloads --gs-dir tennis=$G/tennis_payloads --gs-dir hockey_nhl=$G/hockey_nhl_payloads --out $D/coverage.json --tail-mb 1500 | cut -c1-1500
```
(If `pmdota` has no `markets.jsonl` in that folder the line is empty; say so. Run one scan at a time, after P85/P84a, before P83 if disk allows; stops at your 10 GB floor.)
2. Paste the output and `sha256sum $D/coverage.json` under `## P87 coverage matrix (20 Nov)` in `agent/status/goalserve.md`.
3. **Drop basketball (restart of capture):** PR #455 (merged) removes basketball polling and storing. Do it **between matches, ideally in a quiet gap**: `git -C /root/pkarbs fetch -q origin claude/project-thread-vg2ckg`, deploy `live/goalserve/capture_store_all.py` as for the previous restart, restart the tmux `goalserve` capture, then paste `pgrep -f capture_store_all`, and after 3 minutes `ls -l --time-style=full-iso $G/esports_payloads | tail -2; ls -l --time-style=full-iso $G/tennis_payloads | tail -2; ls -l --time-style=full-iso $G/hockey_nhl_payloads | tail -2` (all three must show a file written in the last 3 minutes; no `basketball_payloads` file may grow). Keep `basketball_payloads` on disk for now; I will confirm in writing before you delete it.
