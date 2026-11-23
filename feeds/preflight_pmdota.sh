#!/usr/bin/env bash
# R-058 pre-flight for feeds/pm_dota_books.js. Run by IT on the target host BEFORE any (re)start; any FAIL = do not start.
# usage: preflight_pmdota.sh [SECONDS=75]  -> exit 0 PASS, 1 FAIL, 2 UNVERIFIED (no market inside its window, live data cannot be proved)
# Uses a scratch dir (mktemp), never the production dir. Env GAMMA_URL/CLOB_URL pass through (tests).
set -u
SEC=${1:-75}; D=$(dirname "$0"); T=$(mktemp -d); rc=0
END=$(date -u -d "+${SEC} seconds" +%Y-%m-%dT%H:%M:%SZ)
node "$D/pm_dota_books.js" "$T" "$END" >/dev/null 2>&1 & P1=$!
sleep 3
node "$D/pm_dota_books.js" "$T" "$END" >/dev/null 2>&1; R2=$?
[ "$R2" = 3 ] && echo "PASS single-instance lock: second copy refused (exit 3)" || { echo "FAIL single-instance lock: second copy exit $R2 (need 3)"; rc=1; }
wait $P1
LINE=$(grep -E "discovery markets [0-9]+ tokens [0-9]+" "$T/recorder.log" | tail -1)
python3 - "$T" "$LINE" <<'PY' || rc=$?
import sys,json,re,datetime,os
t,line=sys.argv[1],sys.argv[2]
m=re.search(r"markets (\d+) tokens (\d+)",line or "")
if not m or int(m.group(2))==0 or int(m.group(2))!=2*int(m.group(1)):
    print("FAIL tokens: need >0 and = 2 x markets; log line:",repr(line)); sys.exit(1)
print("PASS tokens:",m.group(2),"for",m.group(1),"markets")
now=datetime.datetime.now(datetime.timezone.utc).timestamp()
inwin=set()
for l in open(os.path.join(t,"markets.jsonl")):
    r=json.loads(l)
    if r.get("start"):
        s=datetime.datetime.fromisoformat(r["start"].replace("Z","+00:00")).timestamp()
        if s-1200<=now<=s+18000: inwin.add(r["cond"])
bp=os.path.join(t,"books.jsonl"); rows=[json.loads(x) for x in open(bp)] if os.path.exists(bp) else []
if not inwin:
    print("UNVERIFIED live data: no market inside its [start-20 min, +5 h] window now; 60 s of real rows cannot be proved"); sys.exit(2)
miss=[c for c in inwin if len({r["token"] for r in rows if r["cond"]==c})!=2]
if miss: print("FAIL live data: %d of %d in-window markets lack rows for both tokens"%(len(miss),len(inwin))); sys.exit(1)
print("PASS live data: both tokens' rows for all",len(inwin),"in-window markets,",len(rows),"rows")
PY
echo "scratch dir: $T"; exit $rc
