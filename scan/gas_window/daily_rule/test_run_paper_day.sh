#!/usr/bin/env bash
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); got=$(DRY_RUN=1 OUT=/o bash "$HERE/run_paper_day.sh" 2026-11-21)
want="python3 $HERE/paper_day.py --date 2026-11-21 --books /o/us-gas-price-on-november-21-2026.books.jsonl --page /o/aaa_page_2026-11-21.jsonl --out-dir /o/paper"
if [ "$got" = "$want" ]; then echo "PASS"; echo "1 of 1 tests pass"; else echo "FAIL got [$got]"; exit 1; fi
