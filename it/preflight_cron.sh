#!/bin/bash
# Hourly cron wrapper for the live preflight (Goalserve thread, 19 Nov 2026). No model, no credentials. Writes the latest preflight to a fixed file and appends to a history log.
# Install once: 20 * * * * bash /root/ship/preflight_cron.sh      (the heartbeat at :00 of the next hour can append `cat $LOGD/PREFLIGHT-LATEST.txt` to its commit)
V=/mnt/HC_Volume_107257520; LOGD=$V/pkarbs/scratch/goalserve-daily-logs; mkdir -p "$LOGD"
git -C /root/pkarbs fetch -q origin reviewer 2>/dev/null && git -C /root/pkarbs show origin/reviewer:it/goalserve_preflight.sh > "$LOGD/goalserve_preflight.sh" 2>/dev/null
[ -s "$LOGD/goalserve_preflight.sh" ] || { echo "$(date -u +%FT%TZ) preflight script missing" >> "$LOGD/PREFLIGHT-HISTORY.log"; exit 1; }
bash "$LOGD/goalserve_preflight.sh" > "$LOGD/PREFLIGHT-LATEST.txt.tmp" 2>&1; mv "$LOGD/PREFLIGHT-LATEST.txt.tmp" "$LOGD/PREFLIGHT-LATEST.txt"
{ date -u +%FT%TZ; grep -E '^(FAIL|VERDICT)' "$LOGD/PREFLIGHT-LATEST.txt"; } >> "$LOGD/PREFLIGHT-HISTORY.log"
