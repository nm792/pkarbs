#!/bin/bash
# Supervisor for the mentions WS paper test on Prime (R-050/R-051). Run once under IT's caps; restarts the python process 5 s after any exit and records each exit.
# Usage (IT): nohup nice -n 10 bash mentions_pm_ws_paper_run.sh >/dev/null 2>&1 &   (use your standard memory/CPU cap wrapper around this command)
set -u
V=${V:-/mnt/HC_Volume_107257520}; GIT=${GITDIR:-/root/pkarbs}; BR=${BR:-reviewer}; O=$V/pkarbs/mentions/ws-paper; S=$V/pkarbs/mentions/daily/state; mkdir -p "$O"
exec 9>"$O/.supervisor.lock"; flock -n 9 || { echo "$(date -u +%FT%TZ) second supervisor refused" >> "$O/supervisor.log"; exit 1; }
# R-058 gate: a PASS pre-flight (mentions_pm_ws_paper.py --preflight) newer than 6 h must exist, else nothing starts
python3 -I -c "import json,sys,time; r=json.load(open(sys.argv[1])); sys.exit(0 if r.get('ok') and time.time()-r['t']<21600 else 1)" "$O/PREFLIGHT.json" 2>/dev/null || { echo "$(date -u +%FT%TZ) no PASS preflight in the last 6 h; nothing starts" >> "$O/supervisor.log"; exit 1; }
[ -s "$S/events.json" ] || { echo "$(date -u +%FT%TZ) no events.json" >> "$O/supervisor.log"; exit 1; }
for f in mentions_pm_ws_paper.py ws_min.py mentions_pm_daily_scorer.py; do git -C "$GIT" show "origin/$BR:it/$f" > "$O/$f" || { echo "$(date -u +%FT%TZ) show $f failed" >> "$O/supervisor.log"; exit 1; }; done
while true; do
  python3 -I "$O/mentions_pm_ws_paper.py" --scorer "$O/mentions_pm_daily_scorer.py" --state "$S" --out "$O" 2>> "$O/stderr.log"; RC=$?
  echo "$(date -u +%FT%TZ) python exited rc=$RC ; restart in 5 s" >> "$O/supervisor.log"; sleep 5
done
