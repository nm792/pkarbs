#!/usr/bin/env bash
# Daily wrapper for the gas listing waiter (cron: 50 14 * * *, UTC). Starts wait_listing.py for the event that lists TODAY at about 15:00:11Z
# (10:00 ET on D-1 in winter time; it lists at 14:00Z in US summer time, so move the cron to 13:50 from the second Sunday of March 2027).
# usage: run_daily_gas_waiter.sh [RUN_DAY=YYYY-MM-DD, default today UTC]   env: OUT (default /mnt/HC_Volume_107257520/gas) DRY_RUN=1 prints the command only
set -u
DAY=${1:-$(date -u +%F)}
NEXT=$(date -u -d "$DAY +1 day" +%F) || exit 2
SLUG="us-gas-price-on-$(date -u -d "$NEXT" +%B | tr 'A-Z' 'a-z')-$(date -u -d "$NEXT" +%-d)-$(date -u -d "$NEXT" +%Y)"
OUT=${OUT:-/mnt/HC_Volume_107257520/gas}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CMD=(python3 "$HERE/wait_listing.py" --slug "$SLUG" --out "$OUT" --wait-until "${DAY}T16:30:00Z" --record-seconds 5400)
if [ "${DRY_RUN:-0}" = "1" ]; then echo "${CMD[*]}"; exit 0; fi
mkdir -p "$OUT" && exec "${CMD[@]}" > "$OUT/wait-${NEXT//-/}.log" 2>&1
