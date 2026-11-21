#!/usr/bin/env bash
# Daily scorer for the paper run. cron (UTC, winter): 10 16 * * *  and  10 20 * * *   (re-running a day replaces its row; a day is scored only once Gamma shows it resolved)
# usage: run_paper_day.sh [EVENT_DAY=YYYY-MM-DD, default today UTC]   env: OUT (default /mnt/HC_Volume_107257520/gas) DRY_RUN=1 prints the command
set -u
D=${1:-$(date -u +%F)}
SLUG="us-gas-price-on-$(date -u -d "$D" +%B | tr 'A-Z' 'a-z')-$(date -u -d "$D" +%-d)-$(date -u -d "$D" +%Y)"
OUT=${OUT:-/mnt/HC_Volume_107257520/gas}; HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CMD=(python3 "$HERE/paper_day.py" --date "$D" --books "$OUT/$SLUG.books.jsonl" --page "$OUT/aaa_page_${D}.jsonl" --out-dir "$OUT/paper")
if [ "${DRY_RUN:-0}" = "1" ]; then echo "${CMD[*]}"; exit 0; fi
mkdir -p "$OUT/paper" && exec "${CMD[@]}" >> "$OUT/paper/paper_day_${D}.log" 2>&1
