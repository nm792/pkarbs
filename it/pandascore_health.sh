#!/usr/bin/env bash
# PandaScore pipeline health, READ-ONLY, one paste. Usage: bash pandascore_health.sh [V=/mnt/HC_Volume_107257520]
V=${1:-/mnt/HC_Volume_107257520}; now=$(date -u +%s); echo "now $(date -u +%FT%TZ)"
echo "== capture (ll_capture) =="; pgrep -af ll_capture.py | cut -c1-110 || echo "NOT RUNNING"
f=$(ls -t $V/pkarbs/pandascore/raw/pandascore_*.jsonl.gz 2>/dev/null | head -1); [ -n "$f" ] && echo "newest raw file $(basename $f) size $(stat -c %s $f) mtime_age_s $(( now - $(stat -c %Y $f) ))" || echo "NO RAW FILES"
echo "raw hour files since 17 Nov (name size):"; ls -l $V/pkarbs/pandascore/raw/pandascore_20261117* $V/pkarbs/pandascore/raw/pandascore_20261118* $V/pkarbs/pandascore/raw/pandascore_20261119* 2>/dev/null | awk '{print $9, $5}' | sed "s#.*/##"; ls -d /vol2/pandascore/raw 2>/dev/null && ls -l /vol2/pandascore/raw | tail -4 | awk '{print "vol2:", $9, $5}'
echo "== CS2 book recorder pmcs2 =="; pgrep -af pm_cs2_books.js | cut -c1-110 || echo "NOT RUNNING"
b=$V/pkarbs/pmcs2/books.jsonl; if [ -f "$b" ]; then
  echo "books.jsonl bytes $(stat -c %s $b) rows $(wc -l < $b) mtime_age_s $(( now - $(stat -c %Y $b) ))"
  python3 -I - "$b" "$now" <<'P'
import sys, json
b, now = sys.argv[1], int(sys.argv[2]); toks, last15, last = set(), 0, 0
with open(b) as f:
    for l in f:
        try: r = json.loads(l)
        except Exception: continue
        toks.add(r.get("asset")); last = max(last, r.get("recv_ms", 0))
        if r.get("recv_ms", 0) > (now - 900) * 1000: last15 += 1
print("distinct tokens", len(toks), "rows_last_15min", last15, "last_row_age_s", round(now - last / 1000))
P
else echo "NO books.jsonl"; fi
tail -2 $V/pkarbs/pmcs2/recorder.log 2>/dev/null | cut -c1-140
echo "== CS2 probe / loop =="; pgrep -af "live_probe_cs2.py|pandascore_cs2_probe_loop" | cut -c1-140 || echo "none running"
tail -3 $V/pkarbs/probe/probe-loop.log 2>/dev/null; for l in $V/pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.log; do [ -f $l ] && { grep -E "CS2 feeds open|matched PM|PREFLIGHT|FINAL|FAILED|NO live" $l | cut -c1-600 | tail -6; }; done
echo "== disk =="; df -B1 --output=avail $V | tail -1 | awk '{printf "free_GB %.1f\n", $1/1e9}'
echo "== daily look output =="; ls -l $V/pkarbs/scratch/pandascore-daily-cs2/result-cs2-look*.json 2>/dev/null | cut -c1-120 || echo "none yet (look 1 due 20 Nov ~01:00Z)"
