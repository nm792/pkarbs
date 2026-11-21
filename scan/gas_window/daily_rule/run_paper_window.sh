#!/usr/bin/env bash
# Paper-run capture window for the gas `post` rule: for EVENT_DAY D (the date in the market slug) record the AAA page log and the 12 books from 02:40 ET to 04:30 ET on D,
# plus the page log on to 10:00 ET (Reviewer R-002 condition 1: page value + fetch time every poll, 02:45-04:00 ET) and a short second book window 09:50-10:00 ET (R-004: the 10:00 ET markout needs a book). Handles winter/summer time by asking `date` for America/New_York.
# cron (UTC, winter): 35 7 * * *  bash <deploy>/scan/gas_window/daily_rule/run_paper_window.sh      (default D = today UTC; moves to 6:35 UTC in US summer time)
# usage: run_paper_window.sh [EVENT_DAY=YYYY-MM-DD]   env: OUT (default /mnt/HC_Volume_107257520/gas) DRY_RUN=1 prints the commands only
set -u
D=${1:-$(date -u +%F)}
SLUG="us-gas-price-on-$(date -u -d "$D" +%B | tr 'A-Z' 'a-z')-$(date -u -d "$D" +%-d)-$(date -u -d "$D" +%Y)"
iso() { date -u -d "@$(TZ=America/New_York date -d "$D $1" +%s)" +%Y-%m-%dT%H:%M:%SZ; }
S=$(iso 02:40); BE=$(iso 04:30); PE=$(iso 10:00)
BSEC=$(( $(date -u -d "$BE" +%s) - $(date -u -d "$S" +%s) ))
OUT=${OUT:-/mnt/HC_Volume_107257520/gas}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); GW="$HERE/.."
PAGE=("python3" "$HERE/aaa_page_log.py" --out "$OUT/aaa_page_${D}.jsonl" --start "$S" --until "$PE" --interval 30)
BOOKS=("python3" "$GW/pm_gas_books.py" --slug "$SLUG" --out "$OUT" --until "$BE" --interval 1 --max-seconds "$BSEC")
T1=$(iso 09:50)      # second, short book window so the 10:00 ET markout has a book (R-004 item 2); appends to the same books file
LATE=("python3" "$GW/pm_gas_books.py" --slug "$SLUG" --out "$OUT" --until "$PE" --interval 1 --max-seconds 600)
if [ "${DRY_RUN:-0}" = "1" ]; then echo "${PAGE[*]}"; echo "${BOOKS[*]}"; echo "${LATE[*]}"; exit 0; fi
mkdir -p "$OUT"
# wait for the window start (cron fires a little early; never start the logs late)
while [ "$(date -u +%s)" -lt "$(date -u -d "$S" +%s)" ]; do sleep 5; done
"${PAGE[@]}" > "$OUT/aaa_page_${D}.log" 2>&1 &
( while [ "$(date -u +%s)" -lt "$(date -u -d "$T1" +%s)" ]; do sleep 5; done; exec "${LATE[@]}" > "$OUT/paper_books_late_${D}.log" 2>&1 ) &
exec "${BOOKS[@]}" > "$OUT/paper_books_${D}.log" 2>&1
