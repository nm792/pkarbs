#!/bin/bash
# Daily Goalserve look, run by cron at 07:30Z (Goalserve thread, 19 Nov 2026). No model, no credentials in this file.
# Fetches the committed look script, runs it for esports and tennis, keeps the full output in a known folder.
# The box variables the look needs (RSYNC_RSH, BOX_ROOT) must come from the same env file ship_raw.sh uses: set ENVFILE below to it. Never print them.
set -u
V=/mnt/HC_Volume_107257520; GIT=/root/pkarbs; ENVFILE=${ENVFILE:-/root/ship/env}
LOGD=$V/pkarbs/scratch/goalserve-daily-logs; mkdir -p "$LOGD"
[ -r "$ENVFILE" ] && . "$ENVFILE"
D=$(date -u +%F)
git -C "$GIT" fetch -q origin claude/project-thread-vg2ckg || { echo "$D fetch failed" >> "$LOGD/cron-errors.log"; exit 1; }
git -C "$GIT" show origin/claude/project-thread-vg2ckg:feeds/run_daily_look.sh > "$LOGD/run_daily_look.sh" || exit 1
for S in esports tennis; do
  ( cd "$LOGD" && bash "$LOGD/run_daily_look.sh" "$S" > "$LOGD/look-$S-$D.log" 2>&1; echo "exit $? at $(date -u +%FT%TZ)" >> "$LOGD/look-$S-$D.log" )
  tail -c 1200 "$LOGD/look-$S-$D.log" > "$LOGD/LATEST-$S.tail"
done
