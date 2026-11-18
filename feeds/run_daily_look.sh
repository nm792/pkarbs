#!/bin/bash
# Daily look of the signed Goalserve odds-vs-Polymarket test (v2). Usage: run_daily_look.sh esports|tennis
# Reads captures; writes only under $V/pkarbs/scratch/goalserve-daily-<sport>. Never passes --seed, --plant-c or --smoke.
# Needs RSYNC_RSH and BOX_ROOT in the environment for the box copy (never printed). Overrides for tests only: V, GITDIR, NOW_UTC_DATE, MIN_FREE, SKIP_SELFTEST.
set -u
SPORT=${1:-}; V=${V:-/mnt/HC_Volume_107257520}; GITDIR=${GITDIR:-/root/pkarbs}
case "$SPORT" in esports) START=20261118; FLAG="";; tennis) START=20261119; FLAG="--sport tennis";; *) echo "usage: $0 esports|tennis"; exit 2;; esac
G=$V/pkarbs/goalserve; PM1=$V/pkarbs/thesports/final-topics-32295b
X=$V/pkarbs/scratch/goalserve-run-tree; T=$V/pkarbs/scratch/goalserve-daily-$SPORT; mkdir -p "$T/gs" "$V/tmp"
AV=$(df -B1 --output=avail "$V" | tail -1); echo "date $(date -u +%FT%TZ) avail_bytes $AV"
[ "$AV" -gt "${MIN_FREE:-15000000000}" ] || { echo "STOP: data disk free below 15 GB"; exit 1; }
rm -rf "$X" && mkdir -p "$X" && git -C "$GITDIR" fetch -q origin claude/project-thread-vg2ckg && git -C "$GITDIR" archive origin/claude/project-thread-vg2ckg feeds | tar -x -C "$X" || { echo "STOP: export failed"; exit 1; }
echo "commit $(git -C "$GITDIR" log -1 --format=%H origin/claude/project-thread-vg2ckg)"; cd "$X" || exit 1
sha256sum feeds/goalserve_odds_vs_pm_v2.py feeds/test_goalserve_odds_vs_pm_v2.py
if [ -z "${SKIP_SELFTEST:-}" ]; then TMPDIR=$V/tmp python3 -I feeds/test_goalserve_odds_vs_pm_v2.py | tail -2; fi
# days START .. yesterday (UTC)
TODAY=${NOW_UTC_DATE:-$(date -u +%Y%m%d)}; DAYS=(); d=$START
while [ "$d" -lt "$TODAY" ]; do DAYS+=("$d"); d=$(date -u -d "$d +1 day" +%Y%m%d); done
K=${#DAYS[@]}; echo "sport $SPORT look_expected $K days ${DAYS[*]:-none}"; [ "$K" -ge 1 ] || { echo "STOP: no complete day yet"; exit 1; }
if [ -n "${RSYNC_RSH:-}" ] && [ -n "${BOX_ROOT:-}" ]; then
  rsync -a --include="${SPORT}_*.jsonl.gz" --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/${SPORT}_payloads/" "$T/gs/" || echo "WARN: box copy failed"
fi
cp -n "$G/${SPORT}_payloads/${SPORT}_"*.jsonl.gz "$T/gs/" 2>/dev/null
F=(); for d in "${DAYS[@]}"; do F+=(--files "$T/gs/${SPORT}_${d}*.jsonl.gz"); echo "hour files $d: $(ls "$T"/gs/${SPORT}_${d}*.jsonl.gz 2>/dev/null | wc -l)"; done
echo "poll logs: $(ls "$G"/goalserve_20*.jsonl | tr '\n' ' ')"
echo "PM last book row: $(tail -n 1 "$PM1/books.jsonl" 2>/dev/null | cut -c1-160)"; du -sh "$T/gs"
OUT=$T/result-$SPORT-look$K.json
TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 7200 python3 -I feeds/goalserve_odds_vs_pm_v2.py $FLAG "${F[@]}" --poll-log "$G/goalserve_20*.jsonl" --pm "$PM1" \
  --clock-note "Polymarket recorder and Goalserve capture both run on Prime; chrony offset not measured. Single-host reading." --out "$OUT" > "$T/run-$SPORT-look$K.log" 2>&1
echo "run exit $? at $(date -u +%FT%TZ)"; tail -c 500 "$T/run-$SPORT-look$K.log" | grep -i -E "traceback|error|STOP|poll log ends|missing" ; sha256sum "$OUT"
python3 -I - "$OUT" <<'P'
import json, sys
j = json.load(open(sys.argv[1]))
for k in ("sport", "smoke_not_a_result", "look", "n_max", "c_bm", "data_through_utc", "plant_c", "seed", "files", "goalserve_events_total", "drops"):
    print(k, json.dumps(j.get(k)))
a = j["audit"]; print("audit.counters", json.dumps(a["counters"])); print("audit.hour_files", json.dumps(a.get("hour_files"))); print("audit.league_prefixes_seen", json.dumps(a["league_prefixes_seen"])); print("audit.bm_values", json.dumps(a["bm_values"]))
for l in j.get("plain_summary") or []: print(l)
for n, c in j["cells"].items():
    if c.get("role", "").startswith("primary"):
        print("CELL", n, json.dumps({k: c.get(k) for k in ("role", "n_matches_used", "information_time", "boundary_z", "z_eq", "mean_d_per_match", "plants_ok", "plant_recovery", "post_real", "pre_real", "post_placebo", "pre_placebo", "excluded_counts", "matches_by_day", "matches_cumulative_by_day", "verdict")}))
print("first20_events_biggest_cell", json.dumps(j.get("first20_events_biggest_cell")))
P
