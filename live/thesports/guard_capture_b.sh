#!/bin/bash
# P9 restart guard for thesports-capture-b — OPEN row P9 (pkarbs), Type A / charter clause 22A.
# Cron runs this every 5 min: if live/thesports/capture.py is not running, relaunch the
# same command line as a transient unit WITH the TheSports env file.
# Why the env file: the 17:06:03Z transient launch had an empty Environment, so capture.py
# logged 'thesports_no_creds' and ts_mqtt/ts_poll stopped (last ts_mqtt row 17:05:32Z).
# Why no `timeout 552000` wrapper on relaunch: the urgent note of 13 Nov 17:35Z (Type A)
# asks for the timeout removed; capture.py already bounds itself (END = start + 160 h) and
# this guard relaunches it when it exits, so an external timer only cuts a run short.
# Revert: delete this script's crontab line (backup /root/crontab.pre-p9-guard-<stamp>.txt)
# then `rm /root/pkarbs/live/thesports/guard_capture_b.sh`. While capture.py is alive this
# script exits without acting.
set -u
LOG=/var/log/thesports_capture_guard.log
UNIT=thesports-capture-b
ENVF=/etc/pkarbs/thesports.env
SCRIPT=/root/pkarbs/live/thesports/capture.py
OUT=/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b

exec 9>/run/thesports_capture_guard.lock
flock -n 9 || exit 0

# Process-absence check: read /proc cmdlines directly (never pgrep -f, which matches
# the checker itself).
alive=0
for p in /proc/[0-9]*; do
  [ -r "$p/cmdline" ] || continue
  cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null || true)
  case "$cmd" in
    *"python3 -I $SCRIPT"*) alive=1; break ;;
  esac
done

if [ "$alive" = 1 ]; then
  [ "${GUARD_VERBOSE:-0}" = "1" ] && echo "$(date -u +%FT%TZ) ALIVE (no action)"
  exit 0
fi

echo "$(date -u +%FT%TZ) ABSENT - relaunching $UNIT with env $ENVF" >> "$LOG"
systemctl reset-failed "$UNIT" >/dev/null 2>&1 || true
if systemd-run --quiet --unit="$UNIT" -p EnvironmentFile="$ENVF" \
    python3 -I "$SCRIPT" "$OUT" 160 --share "$OUT/share" >> "$LOG" 2>&1; then
  echo "$(date -u +%FT%TZ) relaunched $UNIT ok" >> "$LOG"
else
  rc=$?
  echo "$(date -u +%FT%TZ) RELAUNCH FAILED rc=$rc" >> "$LOG"
  exit "$rc"
fi
