#!/bin/bash
# Each check can fail. Run: bash test_ps_cs2_daily_look_cron.sh <path to ps_cs2_daily_look_cron.sh>
set -u; S=$1; T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git init -q "$T/up" && git -C "$T/up" checkout -q -b b1 && mkdir "$T/up/feeds"
printf '#!/bin/bash\necho STUB-RAN V=$V\nexit 7\n' > "$T/up/feeds/run_ps_cs2_daily_look.sh"
git -C "$T/up" add . && git -C "$T/up" -c user.name=t -c user.email=t@t commit -qm s
git clone -q "$T/up" "$T/clone"; mkdir "$T/V"
V=$T/V GITDIR=$T/clone BR=b1 ENVFILE=$T/none bash "$S"
L=$T/V/pkarbs/scratch/pandascore-daily-logs; D=$(date -u +%F)
grep -q "STUB-RAN" "$L/look-cs2-$D.log" || { echo "FAIL: wrapper not run"; exit 1; }
grep -q "exit 7 at" "$L/look-cs2-$D.log" || { echo "FAIL: exit code not recorded"; exit 1; }
[ -s "$L/LATEST-cs2.tail" ] || { echo "FAIL: no LATEST tail"; exit 1; }
rm -rf "$T/V/pkarbs"; V=$T/V GITDIR=$T/clone BR=nosuch ENVFILE=$T/none bash "$S"; rc=$?
[ "$rc" -ne 0 ] && grep -q "fetch failed" "$T/V/pkarbs/scratch/pandascore-daily-logs/cron-errors.log" || { echo "FAIL: bad branch not caught"; exit 1; }
echo "PASS (4 checks, each able to fail)"
