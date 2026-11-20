#!/bin/bash
# Daily cron for the Polymarket mentions forward scorer (mentions thread, 20 Nov 2026). Suggested: 00:20Z daily. No keys, read-only public APIs, no orders.
# Fetches the committed scorer from the reviewer branch and runs it. Output: $V/pkarbs/mentions/daily/{mentions_pm_daily.csv,LATEST.txt,mentions_pm_events_<date>.json}
set -u
V=${V:-/mnt/HC_Volume_107257520}; GIT=${GITDIR:-/root/pkarbs}; BR=${BR:-reviewer}
D=$(date -u +%F); O=$V/pkarbs/mentions/daily; mkdir -p "$O/state"
git -C "$GIT" fetch -q origin "$BR" || { echo "$D fetch failed" >> "$O/cron-errors.log"; exit 1; }
git -C "$GIT" show "origin/$BR:it/mentions_pm_daily_scorer.py" > "$O/mentions_pm_daily_scorer.py" || { echo "$D show failed" >> "$O/cron-errors.log"; exit 1; }
BOOKS=${BOOKS:-$V/pkarbs/mentions}
python3 -I "$O/mentions_pm_daily_scorer.py" --state "$O/state" --out "$O" --books "$BOOKS" > "$O/run-$D.log" 2>&1
echo "exit $? at $(date -u +%FT%TZ)" >> "$O/run-$D.log"
tail -c 1500 "$O/run-$D.log" > "$O/LATEST.tail"
