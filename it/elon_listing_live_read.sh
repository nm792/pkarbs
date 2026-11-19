#!/bin/bash
# READ-ONLY live read of the Elon listing recorder: pid, 60 s file growth, newest event, snapshot cadence. Paste the whole output. DOWN = fix within 15 min or name the blocker.
V=${V:-/mnt/HC_Volume_107257520}; OUT=${OUT:-$V/elon-listing}
D=$(ls -dt "$OUT"/*/ 2>/dev/null | head -1); B=${D}books.jsonl; T=${D}trades.jsonl
sz(){ stat -c %s "$1" 2>/dev/null || echo 0; }
b1=$(sz "$B"); t1=$(sz "$T"); sleep 60; b2=$(sz "$B"); t2=$(sz "$T")
echo "now $(date -u +%FT%TZ) free_GB $(df -BG --output=avail "$V" | tail -1 | tr -dc 0-9)"
echo "recorder pid=$(pgrep -f 'elon_listing.py record' | head -1) newest_event_dir=${D:-none}"
echo "books.jsonl bytes=$b2 grew_60s=$((b2-b1)) $([ $((b2-b1)) -gt 0 ] && echo OK || echo DOWN-or-between-listings)"
echo "trades.jsonl bytes=$t2 grew_60s=$((t2-t1))"
[ -n "$D" ] && python3 - "$B" <<'P'
import json,sys
s=[json.loads(l) for l in open(sys.argv[1])]
print("snapshots",len(s),"first",s[0]["t_local"],"last",s[-1]["t_local"]);g=[s[i+1]["t_local"]-s[i]["t_local"] for i in range(max(len(s)-31,0),len(s)-1)]
print("last-30 gaps median %.2fs max %.2fs"%(sorted(g)[len(g)//2],max(g)) if g else "too few snapshots")
P
echo "seen: $(cat $OUT/seen.json 2>/dev/null)"; echo "errors in log (last 200 lines): $(journalctl -u elon-listing.service -n 200 --no-pager 2>/dev/null | grep -c -E 'error|Traceback')"
