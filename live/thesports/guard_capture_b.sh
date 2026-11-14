#!/bin/bash
# P9 restart guard for thesports-capture-b — OPEN row P9 (pkarbs), Type A / charter clause 22A.
# (IT reply 13 Nov 18:10Z merged #311/#312 item 2 into P9.)
# Cron runs this every 5 min:
#   1. capture.py not running -> relaunch with /etc/pkarbs/thesports.env
#   2. newest row older than $GUARD_MAX_AGE (default 600 s) across books/pmws/ts_mqtt/log
#      -> restart (TERM the capture pids, then relaunch), every restart logged
# ts_poll is excluded from the freshness set: it is written only when a polled body
# changes, so its age is not a liveness signal.
# P9 addendum (OPEN row P11, note #315 item 4, 14 Nov): the freshness set now includes
# trades, and the PM trade recorder (thesports-pmtrades, pm_trades_capture.py) is
# process-guarded here the same way capture.py is - absent -> relaunch.
# Revert for this addendum: cp guard_capture_b.sh.bak-p11-<stamp> guard_capture_b.sh
# Why the env file: the 17:06:03Z transient launch had an empty Environment, so capture.py
# logged 'thesports_no_creds' and ts_mqtt/ts_poll stopped (last ts_mqtt row 17:05:32Z).
# No `timeout 552000` on relaunch (#311 item 1): capture.py bounds itself at 160 h and this
# guard relaunches it when it exits, so an external timer only cuts a run short.
# Revert: delete this script's crontab line (backup /root/crontab.pre-p9-guard-20261113T1818Z.txt)
# then `rm /root/pkarbs/live/thesports/guard_capture_b.sh`. While capture.py is healthy this
# script exits without acting.
set -u
LOG=/var/log/thesports_capture_guard.log
UNIT=thesports-capture-b
ENVF=/etc/pkarbs/thesports.env
SCRIPT=/root/pkarbs/live/thesports/capture.py
TSCRIPT=/root/pkarbs/live/thesports/pm_trades_capture.py
TUNIT=thesports-pmtrades
OUT=/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b
MAX_AGE=${GUARD_MAX_AGE:-600}
DRYRUN=${GUARD_DRYRUN:-0}

exec 9>/run/thesports_capture_guard.lock
flock -n 9 || exit 0

log() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }

# PM trade recorder (note #315 item 1): absent -> relaunch with the same output dir.
trades_pids() {
  local p cmd
  for p in /proc/[0-9]*; do
    [ -r "$p/cmdline" ] || continue
    cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null || true)
    case "$cmd" in *"$TSCRIPT"*) echo "${p#/proc/}" ;; esac
  done
}

trades_check() {
  if [ -n "$(trades_pids)" ]; then return 0; fi
  if [ "$DRYRUN" = "1" ]; then log "DRYRUN: $TUNIT absent, would relaunch"; return 0; fi
  systemctl reset-failed "$TUNIT" >/dev/null 2>&1 || true
  if systemd-run --quiet --unit="$TUNIT" python3 -I "$TSCRIPT" "$OUT" --interval 30 >> "$LOG" 2>&1; then
    log "relaunched $TUNIT ok"
  else
    log "TRADES RELAUNCH FAILED rc=$?"
  fi
}

# Process check: read /proc cmdlines directly (never pgrep -f, which matches the checker).
capture_pids() {
  local p cmd
  for p in /proc/[0-9]*; do
    [ -r "$p/cmdline" ] || continue
    cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null || true)
    case "$cmd" in *"python3 -I $SCRIPT"*) echo "${p#/proc/}" ;; esac
  done
}

relaunch() {
  systemctl reset-failed "$UNIT" >/dev/null 2>&1 || true
  if systemd-run --quiet --unit="$UNIT" -p EnvironmentFile="$ENVF" \
      python3 -I "$SCRIPT" "$OUT" 160 --share "$OUT/share" >> "$LOG" 2>&1; then
    log "relaunched $UNIT ok"
    return 0
  fi
  rc=$?
  log "RELAUNCH FAILED rc=$rc"
  return "$rc"
}

trades_check          # runs every tick, before any exit path below
PIDS=$(capture_pids)
if [ -z "$PIDS" ]; then
  log "ABSENT - relaunching $UNIT with env $ENVF"
  relaunch
  exit $?
fi

newest=0
for f in books pmws ts_mqtt log trades; do
  p="$OUT/$f.jsonl"
  [ -f "$p" ] || continue
  m=$(stat -c %Y "$p" 2>/dev/null || echo 0)
  [ "$m" -gt "$newest" ] && newest=$m
done
if [ "$newest" -gt 0 ]; then
  age=$(( $(date -u +%s) - newest ))
  if [ "$age" -gt "$MAX_AGE" ]; then
    if [ "$DRYRUN" = "1" ]; then
      echo "$(date -u +%FT%TZ) STALE ${age}s > ${MAX_AGE}s - DRYRUN, would restart $UNIT"
      exit 0
    fi
    log "STALE ${age}s > ${MAX_AGE}s across books/pmws/ts_mqtt/log - restarting $UNIT"
    for pid in $PIDS; do kill -TERM "$pid" 2>/dev/null || true; done
    i=0
    while [ -n "$(capture_pids)" ] && [ "$i" -lt 10 ]; do sleep 1; i=$((i + 1)); done
    relaunch
    exit $?
  fi
  [ "${GUARD_VERBOSE:-0}" = "1" ] && echo "$(date -u +%FT%TZ) ALIVE age=${age}s"
  exit 0
fi
[ "${GUARD_VERBOSE:-0}" = "1" ] && echo "$(date -u +%FT%TZ) ALIVE (no stream files to age)"
exit 0
