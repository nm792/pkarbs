#!/bin/bash
# Daily PandaScore CS2 look, run by cron at 01:15Z (PandaScore thread, 19 Nov 2026). No model, no credentials in this file.
# Fetches the committed, hash-pinned wrapper feeds/run_ps_cs2_daily_look.sh from the default branch and runs it. The wrapper itself refuses before a UTC day has closed.
# RSYNC_RSH and BOX_ROOT (for the storage-box copy of shipped raw hour files) must come from the same env file ship_raw.sh uses: set ENVFILE. Never print them.
set -u
V=${V:-/mnt/HC_Volume_107257520}; GIT=${GITDIR:-/root/pkarbs}; ENVFILE=${ENVFILE:-/root/ship/ship.env}; BR=${BR:-claude/project-thread-vg2ckg}
LOGD=$V/pkarbs/scratch/pandascore-daily-logs; mkdir -p "$LOGD"
[ -r "$ENVFILE" ] && . "$ENVFILE"
D=$(date -u +%F)
git -C "$GIT" fetch -q origin "$BR" || { echo "$D fetch failed" >> "$LOGD/cron-errors.log"; exit 1; }
git -C "$GIT" show "origin/$BR:feeds/run_ps_cs2_daily_look.sh" > "$LOGD/run_ps_cs2_daily_look.sh" || { echo "$D show failed" >> "$LOGD/cron-errors.log"; exit 1; }
( cd "$LOGD" && GITDIR="$GIT" V="$V" bash "$LOGD/run_ps_cs2_daily_look.sh" > "$LOGD/look-cs2-$D.log" 2>&1; echo "exit $? at $(date -u +%FT%TZ)" >> "$LOGD/look-cs2-$D.log" )
tail -c 1500 "$LOGD/look-cs2-$D.log" > "$LOGD/LATEST-cs2.tail"
