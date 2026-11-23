#!/bin/bash
# Keep-alive for pm_sport_books.js (R-057 b). Matches the recorder by PIDFILE ($OUT/recorder.pid + /proc cmdline containing the script name),
# never by an absolute-path pgrep (that missed 'node pm_sport_books.js' and started a 2nd writer on 23 Nov 01:14Z).
# Usage: nba_keepalive.sh <outDir> <endISO> [floorGB=10] [league=nba]   Env START_CMD overrides the launcher (tests). Exit 0 = running or started.
OUT="$1"; END="$2"; FLOOR="${3:-10}"; LEAGUE="${4:-nba}"; DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"; PF="$OUT/recorder.pid"
if [ -f "$PF" ]; then
  P=$(cat "$PF" 2>/dev/null)
  if [ -n "$P" ] && kill -0 "$P" 2>/dev/null && tr '\0' ' ' < "/proc/$P/cmdline" 2>/dev/null | grep -q 'pm_sport_books'; then echo "running pid $P: not relaunched"; exit 0; fi
fi
[ "$(date -u +%s)" -ge "$(date -u -d "$END" +%s)" ] && { echo "past end time $END: not started"; exit 0; }
if [ -n "$START_CMD" ]; then setsid nohup bash -c "$START_CMD" >> "$OUT/stdout.log" 2>&1 < /dev/null &
else setsid nohup node "$DIR/pm_sport_books.js" "$OUT" "$END" "$FLOOR" "$LEAGUE" >> "$OUT/stdout.log" 2>&1 < /dev/null &
fi
echo "started pid $!"
