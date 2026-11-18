#!/usr/bin/env bash
# CS2 #422 runner. Exploratory (all stored data), UNCHECKED. Run from the repo root on origin/claude/project-thread-vg2ckg (feeds/ps_lead_test.py is the checker-signed file).
# One command:  bash it/REPLY-2026-11-18-2335Z-run_cs2_422.sh
# Writes agent/status/pandascore-cs2-422-*.json and .log. Commit each file as soon as it exists (partial outputs).
set -u
RAW=/mnt/HC_Volume_107257520/pkarbs/pandascore/raw
OUT=agent/status; mkdir -p "$OUT"
# every directory that holds BOTH markets.jsonl(.gz) and books.jsonl(.gz); the test matches markets by team names
PMARGS=""
for d in $(find /mnt/HC_Volume_107257520 /vol2 -maxdepth 6 -type d 2>/dev/null); do
  ls "$d"/markets.jsonl* >/dev/null 2>&1 && ls "$d"/books.jsonl* >/dev/null 2>&1 && PMARGS="$PMARGS --pm $d"
done
echo "PM dirs used:$PMARGS" | tee "$OUT/pandascore-cs2-422-pmdirs.log"
date -u +"start %FT%TZ" | tee -a "$OUT/pandascore-cs2-422-pmdirs.log"
python3 -I feeds/ps_lead_test.py --ps "$RAW" $PMARGS --out "$OUT/pandascore-cs2-422-plain.json" > "$OUT/pandascore-cs2-422-plain.log" 2>&1
echo "plain exit $?" >> "$OUT/pandascore-cs2-422-pmdirs.log"
python3 -I feeds/ps_lead_test_cs2_latency.py --ps "$RAW" $PMARGS --out "$OUT/pandascore-cs2-422-latency.json" > "$OUT/pandascore-cs2-422-latency.log" 2>&1
echo "latency exit $?" >> "$OUT/pandascore-cs2-422-pmdirs.log"
date -u +"end %FT%TZ" >> "$OUT/pandascore-cs2-422-pmdirs.log"
