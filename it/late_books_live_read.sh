#!/bin/bash
# READ-ONLY live read of the late-books recorder: pid, 60 s growth of today's file, last snapshot, last-5 lines. Paste the whole output. Growth is only expected inside a window (+-60 s around T-3h/T-1h/T-30m); between windows check the pid and the file mtime.
V=${V:-/mnt/HC_Volume_107257520}; OUT=${OUT:-$V/late-books}
F=$(ls -t "$OUT"/late_books_*.jsonl 2>/dev/null | head -1); sz(){ stat -c %s "$1" 2>/dev/null || echo 0; }
b1=$(sz "$F"); sleep 60; b2=$(sz "$F")
echo "now $(date -u +%FT%TZ) free_GB $(df -BG --output=avail "$V" | tail -1 | tr -dc 0-9)"
echo "recorder pid=$(pgrep -f 'late_books.py record' | head -1) file=${F:-none} bytes=$b2 grew_60s=$((b2-b1)) mtime_age_s=$(( $(date +%s) - $(stat -c %Y "${F:-/nonexistent}" 2>/dev/null || echo 0) ))"
[ -n "$F" ] && tail -n 5 "$F" | python3 -c "
import sys,json
for l in sys.stdin:
    r=json.loads(l); print(r.get('series'),r.get('lead_h'),'hours_to_end',round(r.get('hours_to_end',0),3),'ask',r.get('ask'),'depth02',r.get('depth02'),'latency_s',round(r.get('latency_s',0),2),r.get('error',''))"
echo "errors in log (last 200 lines): $(journalctl -u late-books.service -n 200 --no-pager 2>/dev/null | grep -c -E 'error|Traceback')"
