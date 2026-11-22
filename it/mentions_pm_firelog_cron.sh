#!/bin/bash
# Every 2 minutes (cron: */2 * * * *). Mentions PM firelog: own-token ask ladders when the 10c rule fires on new mention markets, paper fills at $200 (R-031). No keys, no orders.
set -u
V=${V:-/mnt/HC_Volume_107257520}; GIT=${GITDIR:-/root/pkarbs}; BR=${BR:-reviewer}
O=$V/pkarbs/mentions/daily; F=$V/pkarbs/mentions/firelog; mkdir -p "$F" "$O/state"; D=$(date -u +%F)
[ -s "$O/state/events.json" ] || { echo "$D $(date -u +%T) no events.json (run mentions_pm_daily_cron.sh first)" >> "$F/cron-errors.log"; exit 1; }
git -C "$GIT" fetch -q origin "$BR" || { echo "$D $(date -u +%T) fetch failed" >> "$F/cron-errors.log"; exit 1; }
for f in mentions_pm_firelog.py mentions_pm_daily_scorer.py; do git -C "$GIT" show "origin/$BR:it/$f" > "$F/$f" || { echo "$D show $f failed" >> "$F/cron-errors.log"; exit 1; }; done
timeout 100 python3 -I "$F/mentions_pm_firelog.py" --scorer "$F/mentions_pm_daily_scorer.py" --state "$O/state" --out "$F" >> "$F/run-$D.log" 2>&1
echo "exit $? at $(date -u +%FT%TZ)" >> "$F/run-$D.log"
# scoring once a day at 00:30Z
if [ "$(date -u +%H%M)" = "0030" ]; then python3 -I "$F/mentions_pm_firelog.py" --scorer "$F/mentions_pm_daily_scorer.py" --state "$O/state" --out "$F" --score > "$F/score-$D.log" 2>&1; fi
