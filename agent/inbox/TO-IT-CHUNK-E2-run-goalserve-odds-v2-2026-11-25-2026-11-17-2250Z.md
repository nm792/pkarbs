# CHUNK E2: run the signed Goalserve odds v2 test on the 18 to 24 Nov data. Read-only. Posted 17 Nov 2026 22:50Z, RUN ON 25 NOV (after 24 Nov 23:59Z)

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve esports odds move before the Polymarket price.

**2. Where we stand.** v1 gave "unknown" (audit reviews/AUDIT-goalserve-odds-vs-pm-result-2026-11-17.md). Nick approved a locked rerun on NEW data, card answered 17 Nov 22:15:13Z. v2 code, pre-registration and table are merged: default branch squash 0a32cf9e (PR #401). The rule-to-code table is SIGNED by the "Audit CS2 model" thread (reviews/SIGNOFF-goalserve-odds-vs-pm-v2-rule-to-code-2026-11-17.md, 22 of 22 rows MATCH). Chunk E1 (smoke run on old files) comes first.

**3. The one item that matters.** One run, on 25 Nov, after midnight UTC on 24/25 Nov. **Do NOT run it before then and do NOT pass `--seed` or `--plant-c`.** The rules are locked; results stay UNCHECKED until the independent audit.

**Gates (stop and post the output of the failing line):**
1. data-disk free above 20 GB.
2. E1 posted ALL PASS and `smoke exit 0`.
3. Goalserve hour files `esports_2026111800` to `esports_2026112423` exist: the loop below prints the count, which must be 168 minus the hours capture was down (post the missing hours; do not fill them).
4. A poll log `goalserve_20261118.jsonl` to `goalserve_20261124.jsonl` exists for EACH of the 7 days (a missing day clears every baseline for that day).
5. The Polymarket recorder's books cover the window: list the recorder dir(s) that hold `books.jsonl(.gz)` and `markets.jsonl(.gz)` written 18 to 24 Nov (the recorder's own files, same format as `final-topics-32295b`), and print for each the first and last `ms` of books rows as UTC. If two dirs are needed, pass `--pm` twice. Do not use a markets file that is not the recorder's own.

```bash
set -u
cd /root/pkarbs && git pull --ff-only
V=/mnt/HC_Volume_107257520
T=$V/pkarbs/scratch/goalserve-odds-v2-20261125; mkdir -p $T/gs
date -u +%FT%TZ; df -B1 --output=avail $V | tail -1
[ "$(df -B1 --output=avail $V | tail -1)" -gt 20000000000 ] || { echo "STOP: data disk free below 20 GB"; exit 1; }
git log -1 --format=%H -- feeds/goalserve_odds_vs_pm_v2.py; sha256sum feeds/goalserve_odds_vs_pm_v2.py feeds/test_goalserve_odds_vs_pm_v2.py
python3 -I feeds/test_goalserve_odds_vs_pm_v2.py | tail -2          # ALL PASS, about 3.5 minutes
for d in 18 19 20 21 22 23 24; do ls $V/pkarbs/goalserve/goalserve_202611$d.jsonl || echo "MISSING poll log 202611$d"; done
rsync -a --include='esports_*.jsonl.gz' --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/esports_payloads/" $T/gs/
cp -n $V/pkarbs/goalserve/esports_payloads/esports_*.jsonl.gz $T/gs/
for d in 18 19 20 21 22 23 24; do ls $T/gs/esports_202611${d}*.jsonl.gz; done | wc -l
du -sh $T/gs
# PM_DIRS: fill PM1 (and PM2 if two dirs are needed) from gate 5
PM1=/FILL/IN/recorder/dir/for/18-24/Nov
F=(); P=()
for d in 18 19 20 21 22 23 24; do F+=(--files "$T/gs/esports_202611${d}*.jsonl.gz"); P+=(--poll-log "$V/pkarbs/goalserve/goalserve_202611${d}.jsonl"); done
[ -d "$PM1" ] || { echo "STOP: PM1 not filled in"; exit 1; }
TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 7200 python3 -I feeds/goalserve_odds_vs_pm_v2.py \
  "${F[@]}" "${P[@]}" --pm "$PM1" \
  --clock-note "Polymarket recorder and Goalserve capture both run on Prime; chrony offset <state the value and time>. Single-host reading." \
  --out $T/result-v2.json > $T/run-v2.log 2>&1
echo "v2 exit $? at $(date -u +%FT%TZ)"; sha256sum $T/result-v2.json
```
The script takes `--files` and `--poll-log` repeated, one per day, as built above. Do not pass `--seed` or `--plant-c`.

**Output to post** (append to agent/status/goalserve.md under `## E2 real run (25 Nov)`, and copy `result-v2.json` to `agent/status/goalserve-odds-v2-result-2026-11-25.json`): the date, `df`, commit and sha256 lines, gate 3 to 5 outputs, exit code, then ONLY these printed from the JSON (no interpretation): `plant_c`, `seed`, `files`, `goalserve_events_total`, `drops`, `audit.counters`, `audit.league_prefixes_seen`, `audit.bm_values`, `poll_interval_measured`, and for each cell: role, n_matches, n_events, mean_d_per_match, ci95_match_boot, share_events_real_gt_placebo_pct, plant_detected, min_detectable_effect, ties_d_zero, verdict, plus `first20_events_biggest_cell`.
**Done check:** exit 0, `plant_c` 0.01, `seed` 20261118, result file copied with matching sha256, `payloads_after_poll_gap_gt_10s` printed.
**Order:** 25 Nov 00:30Z or later, ahead of anything else on the data volume; about 30 to 60 minutes of one core.
