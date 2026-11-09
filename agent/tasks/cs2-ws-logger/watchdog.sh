#!/bin/bash
# Every 2 min: restart the logger if it is not running or its last frame is over 90 s old. Single instance via pidfile.
DIR="$HOME/cs2logger"; OUT="$DIR/out"; LOG="$OUT/logger.log"
exec 9>"$DIR/watchdog.lock"; flock -n 9 || exit 0
start() { echo "$(date -u +%FT%TZ) WATCHDOG restart: $1" >> "$LOG"; setsid nohup env NODE_PATH="$HOME/ws_probe/node_modules" HOURS=${HOURS:-12} OUT="$OUT" node "$DIR/logger.js" >> "$DIR/logger.stdout" 2>&1 < /dev/null & }
while [ -f "$DIR/run.flag" ]; do
  if ! pgrep -f "node $DIR/logger.js" >/dev/null && ! pgrep -f "node logger.js" >/dev/null; then start "process not running"; sleep 5;
  else
    LAST=$(tail -n1 "$OUT/cs2_frames.jsonl" 2>/dev/null | python3 -I -c "import sys,json,time;l=sys.stdin.read().strip();print(int(time.time()-json.loads(l)['recv_ms']/1000) if l else 999999)" 2>/dev/null || echo 999999)
    if [ "$LAST" -gt 90 ] && [ "$(date +%s)" -gt "$(stat -c %Y "$OUT/logger.log" 2>/dev/null || echo 0)" ]; then pkill -f "node logger.js"; sleep 2; start "last frame ${LAST}s old"; sleep 5; fi
  fi
  sleep 120
done
