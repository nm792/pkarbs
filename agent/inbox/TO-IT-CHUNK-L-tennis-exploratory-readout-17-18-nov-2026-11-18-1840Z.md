# CHUNK L: exploratory tennis readout on the stored days 17 and 18 Nov (UNCHECKED). Read-only. Posted 18 Nov 2026 18:40Z. URGENT: Nick wants a readout by 20:00Z.

**1. Goal.** Nick (18:19Z): run the fixed test on every stored tennis day tonight, do not wait for the daily looks.
**2. Position.** Tennis has been stored since 17 Nov 09:00Z. The locked tennis looks (chunk K) count from 19 Nov 00:00Z and are untouched by this run. This run reads 17 and 18 Nov one day at a time with the signed test code in `--smoke` mode (one UTC day per run, no completeness refusals). It is exploratory, not pre-registered, not a look, and the output is labelled UNCHECKED; it cannot be a pass.
**3. The one item.** Clean export first (it/REPLY-2026-11-18-URGENT-goalserve-ruling-clean-tree-no-stash.md), then for D in 20261117 and 20261118:
```
V=/mnt/HC_Volume_107257520; G=$V/pkarbs/goalserve; T=$V/pkarbs/scratch/goalserve-explore-tennis; mkdir -p $T/gs
rsync -a --include='tennis_*.jsonl.gz' --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/tennis_payloads/" $T/gs/ ; cp -n $G/tennis_payloads/tennis_2026111[78]*.jsonl.gz $T/gs/ 2>/dev/null
for D in 20261117 20261118; do
 ls $T/gs/tennis_${D}*.jsonl.gz | wc -l
 TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 7200 python3 -I $X/feeds/goalserve_odds_vs_pm_v2.py --smoke --sport tennis --files "$T/gs/tennis_${D}*.jsonl.gz" --poll-log "$G/goalserve_20*.jsonl" --pm $V/pkarbs/thesports/final-topics-32295b --clock-note "exploratory readout, not a look" --out $T/explore-$D.json > $T/explore-$D.log 2>&1; echo "$D exit $?"
 python3 -I - $T/explore-$D.json <<'P'
import json, sys
j = json.load(open(sys.argv[1])); print("day", j["data_through_utc"], "sport", j["sport"], "smoke_not_a_result", j["smoke_not_a_result"], "files", j["files"], "events", j["goalserve_events_total"])
print("counters", json.dumps(j["audit"]["counters"])); print("drops", json.dumps(j["drops"]))
for n, c in j["cells"].items():
    if c.get("role", "").startswith("primary"): print("CELL", n, json.dumps({k: c.get(k) for k in ("n_matches_used", "n_events", "z_eq", "mean_d_per_match", "plants_ok", "plant_recovery", "post_real", "pre_real", "post_placebo", "pre_placebo", "excluded_counts", "verdict")}))
print("top informational cells:", [(n, c.get("n_matches_used"), c.get("z_eq")) for n, c in j["cells"].items() if not c.get("role", "").startswith("primary")][:6])
P
done
```
Post the whole output under `## L tennis exploratory (18 Nov)` in agent/status/goalserve.md. Do not delete the files in `$T`.
**Done check:** both days print `exit 0`, `smoke_not_a_result True` and a `CELL tennis|Match Winner` line. Day 17 starts at 09:00Z and day 18 is partial; say so.
