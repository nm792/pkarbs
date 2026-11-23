#!/bin/bash
# Each check can fail. Run: bash test_mentions_pm_ws_paper_run.sh <path to mentions_pm_ws_paper_run.sh>
set -u; S=$1; T=$(mktemp -d); trap 'pkill -P $$ 2>/dev/null; rm -rf "$T"' EXIT
git init -q "$T/up" && git -C "$T/up" checkout -q -b b1 && mkdir "$T/up/it"
printf 'import sys\nprint("STUB")\nsys.exit(3)\n' > "$T/up/it/mentions_pm_ws_paper.py"; echo x=1 > "$T/up/it/ws_min.py"; echo x=1 > "$T/up/it/mentions_pm_daily_scorer.py"
git -C "$T/up" add . && git -C "$T/up" -c user.name=t -c user.email=t@t commit -qm s; git clone -q "$T/up" "$T/clone"
O=$T/V/pkarbs/mentions/ws-paper; mkdir -p "$O"
V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; grep -q "no PASS preflight" "$O/supervisor.log" || { echo "FAIL: start without preflight not refused"; exit 1; }
python3 -c "import json,time; json.dump(dict(ok=False,t=time.time()),open('$O/PREFLIGHT.json','w'))"; : > "$O/supervisor.log"; V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; grep -q "no PASS preflight" "$O/supervisor.log" || { echo "FAIL: failed preflight not refused"; exit 1; }
python3 -c "import json,time; json.dump(dict(ok=True,t=time.time()-30000),open('$O/PREFLIGHT.json','w'))"; : > "$O/supervisor.log"; V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; grep -q "no PASS preflight" "$O/supervisor.log" || { echo "FAIL: stale preflight not refused"; exit 1; }
python3 -c "import json,time; json.dump(dict(ok=True,t=time.time()),open('$O/PREFLIGHT.json','w'))"; : > "$O/supervisor.log"
V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; grep -q "no events.json" "$O/supervisor.log" || { echo "FAIL: missing events.json not caught"; exit 1; }
mkdir -p "$T/V/pkarbs/mentions/daily/state"; echo '{}' > "$T/V/pkarbs/mentions/daily/state/events.json"
( V=$T/V GITDIR=$T/clone BR=b1 timeout 8 bash "$S" ) ; 
n=$(grep -c "python exited rc=3" "$O/supervisor.log"); [ "$n" -ge 1 ] || { echo "FAIL: exit not recorded"; exit 1; }
[ -s "$O/mentions_pm_ws_paper.py" ] && [ -s "$O/ws_min.py" ] || { echo "FAIL: files not fetched"; exit 1; }
( V=$T/V GITDIR=$T/clone BR=b1 timeout 6 bash "$S" ) & sleep 2; V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; wait
grep -q "second supervisor refused" "$O/supervisor.log" || { echo "FAIL: second supervisor not refused"; exit 1; }
echo "PASS (7 checks, each able to fail)"
