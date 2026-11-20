#!/bin/bash
# Each check can fail. Run: bash test_mentions_pm_daily_cron.sh <path to mentions_pm_daily_cron.sh>
set -u; S=$1; T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git init -q "$T/up" && git -C "$T/up" checkout -q -b b1 && mkdir "$T/up/it"
printf 'import sys\nprint("STUB-RAN", sys.argv[1:])\nsys.exit(7)\n' > "$T/up/it/mentions_pm_daily_scorer.py"
git -C "$T/up" add . && git -C "$T/up" -c user.name=t -c user.email=t@t commit -qm s
git clone -q "$T/up" "$T/clone"; mkdir "$T/V"
V=$T/V GITDIR=$T/clone BR=b1 bash "$S"
O=$T/V/pkarbs/mentions/daily; D=$(date -u +%F)
grep -q "STUB-RAN" "$O/run-$D.log" || { echo "FAIL: scorer not run"; exit 1; }
grep -q "exit 7 at" "$O/run-$D.log" || { echo "FAIL: exit code not recorded"; exit 1; }
grep -q -- "--books" "$O/run-$D.log" || { echo "FAIL: books arg missing"; exit 1; }
[ -s "$O/LATEST.tail" ] || { echo "FAIL: no tail"; exit 1; }
V=$T/V GITDIR=$T/clone BR=nosuch bash "$S"; rc=$?
[ "$rc" -ne 0 ] && grep -q "fetch failed" "$O/cron-errors.log" || { echo "FAIL: bad branch not caught"; exit 1; }
echo "PASS (5 checks, each able to fail)"
