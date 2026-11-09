#!/bin/bash
# Every 2 min: start capture.js for each config label whose window is open and that is not already running.
# Restart it if its frames or books log has been silent for 120 s during the window. Single instance via flock.
DIR="$(cd "$(dirname "$0")" && pwd)"; OUT="${OUT:-$HOME/lolcap/out}"; mkdir -p "$OUT"
exec 9>"$OUT/watchdog.lock"; flock -n 9 || exit 0
[ -f "$OUT/run.flag" ] || exit 0
python3 -I -c "import json,sys; [print(c['label'], c['scheduled_start_utc']) for c in json.load(open(sys.argv[1]))]" "$DIR/config.json" | while read LABEL SCHED; do
  START=$(date -u -d "$SCHED - 90 min" +%s); END=$(date -u -d "$SCHED + 150 min" +%s); NOW=$(date -u +%s)
  [ "$NOW" -ge "$START" ] && [ "$NOW" -le "$END" ] || continue
  LOG="$OUT/${LABEL}_capture.log"
  if pgrep -f "capture.js $DIR/config.json $LABEL " >/dev/null; then
    AGE=$(( NOW - $(stat -c %Y "$OUT/${LABEL}_frames.jsonl" 2>/dev/null || echo 0) ))
    if [ "$AGE" -gt 120 ]; then pkill -f "capture.js $DIR/config.json $LABEL " ; sleep 2; echo "$(date -u +%FT%TZ) WATCHDOG restart $LABEL frames ${AGE}s old" >> "$LOG"; else continue; fi
  fi
  # Bounded: memory cap and a hard time limit at the end of the window.
  setsid nohup systemd-run --scope -p MemoryMax=600M -p MemorySwapMax=0 timeout $(( END - NOW + 60 )) node "$DIR/capture.js" "$DIR/config.json" "$LABEL" 90 150 "$OUT" >> "$OUT/${LABEL}_stdout.log" 2>&1 < /dev/null &
done
