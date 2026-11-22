#!/bin/bash
# Each check can fail. Run: bash test_mentions_pm_firelog_cron.sh <path to mentions_pm_firelog_cron.sh>
set -u; S=$1; T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git init -q "$T/up" && git -C "$T/up" checkout -q -b b1 && mkdir "$T/up/it"
printf 'import sys\nprint("STUB", sys.argv[1:])\nsys.exit(5)\n' > "$T/up/it/mentions_pm_firelog.py"; echo "x=1" > "$T/up/it/mentions_pm_daily_scorer.py"
git -C "$T/up" add . && git -C "$T/up" -c user.name=t -c user.email=t@t commit -qm s
git clone -q "$T/up" "$T/clone"; mkdir -p "$T/V"
F=$T/V/pkarbs/mentions/firelog; O=$T/V/pkarbs/mentions/daily; D=$(date -u +%F)
V=$T/V GITDIR=$T/clone BR=b1 bash "$S"; grep -q "no events.json" "$F/cron-errors.log" || { echo "FAIL: missing events.json not caught"; exit 1; }
mkdir -p "$O/state"; echo '{}' > "$O/state/events.json"
V=$T/V GITDIR=$T/clone BR=b1 bash "$S"
grep -q "STUB.*--out" "$F/run-$D.log" && grep -q "exit 5 at" "$F/run-$D.log" || { echo "FAIL: firelog not run or exit not recorded"; exit 1; }
V=$T/V GITDIR=$T/clone BR=nosuch bash "$S"; rc=$?
[ "$rc" -ne 0 ] && grep -q "fetch failed" "$F/cron-errors.log" || { echo "FAIL: bad branch not caught"; exit 1; }
echo "PASS (4 checks, each able to fail)"
