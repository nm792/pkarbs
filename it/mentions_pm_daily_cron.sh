#!/bin/bash
# Daily cron for the mentions forward scorers (Polymarket 10c arm + Kalshi arms 1 and 2) (mentions thread, 20 Nov 2026). Suggested: 00:20Z daily. No keys, read-only public APIs, no orders.
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
# Kalshi arms 1 and 2 (public read-only Kalshi API, 429 backoff inside mm_forward2.py; takes about 2-3 min per arm)
git -C "$GIT" show "origin/$BR:mentions/forward-arm2/mm_forward2.py" > "$O/mm_forward2.py" || { echo "$D show mm_forward2 failed" >> "$O/cron-errors.log"; exit 1; }
git -C "$GIT" show "origin/$BR:it/kalshi_mentions_daily.py" > "$O/kalshi_mentions_daily.py" || { echo "$D show kalshi failed" >> "$O/cron-errors.log"; exit 1; }
for A in 1 2; do
  python3 -I "$O/kalshi_mentions_daily.py" --mm2 "$O/mm_forward2.py" --out "$O" --arm $A > "$O/run-kalshi-arm$A-$D.log" 2>&1
  echo "exit $? at $(date -u +%FT%TZ)" >> "$O/run-kalshi-arm$A-$D.log"
done
