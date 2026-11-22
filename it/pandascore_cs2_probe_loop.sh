#!/usr/bin/env bash
# CS2 probe supervisor: runs it/REPLY-2026-11-19-live_probe_cs2.py over EVERY live CS2 window until END, so no match window is missed.
# Usage: bash pandascore_cs2_probe_loop.sh <probe.py> <outDir> <endISO> [cycleMinutes=120] [retrySeconds=300]
# The probe exits at once with "NO live CS2 match..." when nothing is live or when PREFLIGHT fails; the loop then waits retrySeconds and tries again.
# Each cycle writes <outDir>/pandascore-cs2-probe-<UTCstamp>.log and .json, and one line to <outDir>/probe-loop.log.
set -u
PROBE=$1; OUT=$2; END=$3; CYC=${4:-120}; RETRY=${5:-300}
mkdir -p "$OUT"; endts=$(date -u -d "$END" +%s)
# do not overlap the already-scheduled --start-at run
while pgrep -f "live_probe_cs2.py --start-at" >/dev/null; do sleep 30; done
while [ "$(date -u +%s)" -lt "$endts" ]; do
  t0=$(date -u +%s); s=$(date -u +%Y%m%dT%H%M%SZ); left=$(( (endts - $(date -u +%s)) / 60 )); m=$(( left < CYC ? left : CYC ))
  [ "$m" -lt 1 ] && break
  python3 -I "$PROBE" --minutes "$m" --out "$OUT/pandascore-cs2-probe-$s.json" > "$OUT/pandascore-cs2-probe-$s.log" 2>&1
  rc=$?; echo "$s exit $rc $(tail -1 "$OUT/pandascore-cs2-probe-$s.log" | cut -c1-160)" >> "$OUT/probe-loop.log"
  # failed, or returned in under 60 s (nothing live / crash): wait before trying again, never spin
  if [ "$rc" -ne 0 ] || [ $(( $(date -u +%s) - t0 )) -lt 60 ]; then sleep "$RETRY"; fi
done
echo "loop done $(date -u +%FT%TZ)" >> "$OUT/probe-loop.log"
