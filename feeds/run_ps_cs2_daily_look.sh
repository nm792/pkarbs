#!/bin/bash
# Daily look of the PandaScore CS2 sequential test (feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md). Usage: run_ps_cs2_daily_look.sh   (look K = complete UTC days since 2026-11-19)
# Reads captures; writes only under $V/pkarbs/scratch/pandascore-daily-cs2. Never passes --seed or --smoke. Modelled on run_daily_look.sh (checker-signed Goalserve wrapper).
# Overrides for tests only: V, GITDIR, NOW_UTC_DATE, MIN_FREE, SKIP_SELFTEST.  Needs RSYNC_RSH and BOX_ROOT for the box copy (never printed).
set -u
V=${V:-/mnt/HC_Volume_107257520}; GITDIR=${GITDIR:-/root/pkarbs}; START=20261119
P=$V/pkarbs/pandascore; PM1=$V/pkarbs/thesports/final-topics-32295b
X=$V/pkarbs/scratch/pandascore-run-tree; T=$V/pkarbs/scratch/pandascore-daily-cs2; mkdir -p "$T/ps" "$V/tmp"
AV=$(df -B1 --output=avail "$V" | tail -1); echo "date $(date -u +%FT%TZ) avail_bytes $AV"
[ "$AV" -gt "${MIN_FREE:-15000000000}" ] || { echo "STOP: data disk free below 15 GB"; exit 1; }
rm -rf "$X" && mkdir -p "$X" && git -C "$GITDIR" fetch -q origin claude/project-thread-vg2ckg && git -C "$GITDIR" archive origin/claude/project-thread-vg2ckg feeds | tar -x -C "$X" || { echo "STOP: export failed"; exit 1; }
echo "commit $(git -C "$GITDIR" log -1 --format=%H origin/claude/project-thread-vg2ckg)"; cd "$X" || exit 1
# pin the signed code: abort if any file differs from the signed hashes
cat > "$X/signed.sha256" <<'H'
75a397605be86534800d973a10050313e608793a0861dfd603c858e6ee87a474  feeds/ps_cs2_daily_look.py
77ea861bdc98fa0c7901b5e41e91922d0995d396ba8f723e8ec8e6720a9ff169  feeds/test_ps_cs2_daily_look.py
4b67d26f6f9f419cd330fdca7ee3c396ed99d5db9ddc56c5370012120c296cb1  feeds/ps_lead_test.py
a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5  feeds/goalserve_odds_vs_pm.py
cbd0f397f09eb92acdd2b6735c093e6a7bed97fcfa4a45dbe32a33f6cb3d1af0  feeds/goalserve_odds_vs_pm_v2.py
H
sha256sum -c "$X/signed.sha256" >/dev/null 2>&1 || { sha256sum feeds/ps_cs2_daily_look.py feeds/test_ps_cs2_daily_look.py feeds/ps_lead_test.py feeds/goalserve_odds_vs_pm.py feeds/goalserve_odds_vs_pm_v2.py; echo "STOP: code differs from the signed hashes; ask the PandaScore thread for the new SIGNED commit"; exit 1; }
if [ -z "${SKIP_SELFTEST:-}" ]; then
  TMPDIR=$V/tmp python3 -I feeds/test_ps_cs2_daily_look.py > "$T/selftest.log" 2>&1; tail -2 "$T/selftest.log"
  [ "$(tail -n 1 "$T/selftest.log")" = "ALL PASS" ] || { echo "STOP: self test did not end with ALL PASS"; exit 1; }
fi
TODAY=${NOW_UTC_DATE:-$(date -u +%Y%m%d)}; DAYS=(); d=$START
while [ "$d" -lt "$TODAY" ]; do DAYS+=("$d"); d=$(date -u -d "$d +1 day" +%Y%m%d); done
K=${#DAYS[@]}; echo "look_expected $K days ${DAYS[*]:-none}"; [ "$K" -ge 1 ] && [ "$K" -le 12 ] || { echo "STOP: no complete day yet, or past look 12"; exit 1; }
# clean copy every time (complete days plus the 8 h before the start for straddle detection); the evlog is copied whole
rm -rf "$T/ps" && mkdir -p "$T/ps"
if [ -n "${RSYNC_RSH:-}" ] && [ -n "${BOX_ROOT:-}" ]; then
  rsync -a --include='pandascore_*.jsonl.gz' --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/pandascore/raw/" "$T/ps/" || echo "WARN: box copy failed"
fi
for d in 20261118 "${DAYS[@]}"; do cp -f "$P/raw/pandascore_${d}"*.jsonl.gz "$T/ps/" 2>/dev/null; done
# remove any hour file at or after the end of the look day (the script reads K from the newest file name)
LASTDAY=${DAYS[$((K-1))]}; for f in "$T/ps/"pandascore_*.jsonl.gz; do b=$(basename "$f" .jsonl.gz); h=${b#pandascore_}; [ "${h:0:8}" -le "$LASTDAY" ] || rm -f "$f"; done
cp -f "$P/events.jsonl.gz" "$T/events.jsonl.gz" || { echo "STOP: no capture event log"; exit 1; }
COPIED=$(date -u +%s); echo "hour files: $(ls "$T/ps" | wc -l) first $(ls "$T/ps" | head -1) last $(ls "$T/ps" | tail -1)"
echo "PM last book row: $(tail -n 1 "$PM1/books.jsonl" 2>/dev/null | cut -c1-160)"; du -sh "$T/ps"
OUT=$T/result-cs2-look$K.json
TMPDIR=$V/tmp nice -n 10 ionice -c3 timeout 7200 python3 -I feeds/ps_cs2_daily_look.py --ps "$T/ps" --pm "$PM1" --evlog "$T/events.jsonl.gz" --copied-at-utc "$COPIED" \
  --clock-note "Polymarket recorder and PandaScore capture both run on Prime; chrony offset not measured. Single-host reading." --out "$OUT" > "$T/run-cs2-look$K.log" 2>&1
echo "run exit $? at $(date -u +%FT%TZ)"; tail -c 600 "$T/run-cs2-look$K.log" | grep -i -E "traceback|error|refus|stopped|copied|lost|truncated"; sha256sum "$OUT"
python3 -I - "$OUT" <<'P'
import json, sys
j = json.load(open(sys.argv[1]))
for k in ("smoke_not_a_result", "look", "n_max", "c_bm", "primary", "data_through_utc", "plant_c", "seed", "hour_files_read", "cs2_events", "drops", "match_exclusions", "capture_silent_matches", "capture_starts_in_window", "plant", "placebo_draws", "event_exclusions"):
    print(k, json.dumps(j.get(k)))
for l in j.get("plain_summary") or []: print(l)
c = j["cells"]["cs2|map|lat0"]; print("PRIMARY", json.dumps({k: c.get(k) for k in c if k != "per_match_d"}))
for n, c in j["cells"].items():
    if n != "cs2|map|lat0": print("INFO", n, json.dumps({k: c.get(k) for k in ("n_matches_used", "n_events", "n_events_with_onset", "z_eq", "median_diff_s", "pct_price_after_feed")}))
print("first20_events_primary", json.dumps(j.get("first20_events_primary")))
P
