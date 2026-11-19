#!/bin/bash
# Read-only health check of the Polymarket Dota recorder (feeds/pm_dota_books.js). One command, prints PASS/FAIL lines. Changes nothing.
# Usage: feeds/check_pmdota.sh [DIR=/mnt/HC_Volume_107257520/pkarbs/pmdota]
D="${1:-/mnt/HC_Volume_107257520/pkarbs/pmdota}"; cd "$D" || { echo "FAIL no dir $D"; exit 1; }
NOW=$(date -u +%s)
echo "now $(date -u +%FT%TZ)"
PID=$(ps -eo pid=,comm=,args= | awk -v d="$D" '$2=="node" && index($0,"pm_dota_books.js") {print $1; exit}')  # comm must be node: never matches the invoking shell
[ -n "$PID" ] && echo "PASS process pid $PID started $(ps -o lstart= -p $PID)" || echo "FAIL recorder process not running"
echo "files:"; ls -l --time-style=full-iso books*.jsonl* markets.jsonl recorder.log 2>/dev/null | tail -12
ROWS=$( ( for f in books.*.jsonl.gz; do [ -f "$f" ] && zcat "$f" 2>/dev/null; done; cat books.jsonl 2>/dev/null ) | wc -l)
echo "total book rows (gz + current): $ROWS"
LAST=$(tail -n 1 books.jsonl 2>/dev/null | python3 -I -c "import sys,json
l=sys.stdin.read().strip()
print(json.loads(l)['recv_ms']//1000 if l else '')" 2>/dev/null)
if [ -n "$LAST" ]; then echo "newest book row age_s $((NOW-LAST))"; else echo "current books.jsonl empty or unreadable"; fi
echo "conds with both tokens in current books.jsonl:"; python3 -I - <<'PY'
import json,collections
c=collections.defaultdict(set)
try:
    for l in open('books.jsonl'):
        try: r=json.loads(l); c[r['cond']].add(r['token'])
        except Exception: pass
except OSError: pass
print(len(c),'conds,',sum(1 for s in c.values() if len(s)==2),'with both tokens')
PY
echo "recorder.log: gamma status lines $(grep -c 'gamma status' recorder.log), book errors $(grep -c 'book error' recorder.log), discover errors $(grep -c 'discover error' recorder.log)"
tail -n 4 recorder.log | cut -c1-160
df -B1 --output=avail "$D" | tail -1 | awk '{printf "avail GB %.2f\n",$1/1e9}'
