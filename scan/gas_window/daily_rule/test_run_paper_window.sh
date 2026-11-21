#!/usr/bin/env bash
# Can-fail test: window times in winter (EST), summer (EDT); a wrong slug or time must fail.
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); ok=0; n=0
chk() { n=$((n+1)); got=$(DRY_RUN=1 OUT=/o bash "$HERE/run_paper_window.sh" "$1"); want="python3 $HERE/aaa_page_log.py --out /o/aaa_page_${1}.jsonl --start ${2} --until ${4} --interval 30
python3 $HERE/../pm_gas_books.py --slug $5 --out /o --until ${3} --interval 1 --max-seconds $6"
  if [ "$got" = "$want" ]; then ok=$((ok+1)); echo "PASS $1"; else echo "FAIL $1: got [$got] want [$want]"; fi; }
# 02:40 EST = 07:40Z, 04:30 EST = 09:30Z (6600 s), 10:00 EST = 15:00Z
chk 2026-11-21 2026-11-21T07:40:00Z 2026-11-21T09:30:00Z 2026-11-21T15:00:00Z us-gas-price-on-november-21-2026 6600
chk 2026-11-22 2026-11-22T07:40:00Z 2026-11-22T09:30:00Z 2026-11-22T15:00:00Z us-gas-price-on-november-22-2026 6600
# summer: 02:40 EDT = 06:40Z
chk 2027-03-15 2027-03-15T06:40:00Z 2027-03-15T08:30:00Z 2027-03-15T14:00:00Z us-gas-price-on-march-15-2027 6600
echo "$ok of $n tests pass"; [ "$ok" = "$n" ]
