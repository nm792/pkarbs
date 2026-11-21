#!/usr/bin/env bash
# Can-fail test: slug and deadline for ordinary, month-end and year-end run days; a wrong slug must fail.
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); ok=0; n=0
chk() { n=$((n+1)); got=$(DRY_RUN=1 OUT=/o bash "$HERE/run_daily_gas_waiter.sh" "$1"); want="python3 $HERE/wait_listing.py --slug $2 --out /o --wait-until ${1}T16:30:00Z --record-seconds 5400"
  if [ "$got" = "$want" ]; then ok=$((ok+1)); echo "PASS $1 -> $2"; else echo "FAIL $1: got [$got] want [$want]"; fi; }
chk 2026-11-20 us-gas-price-on-november-21-2026
chk 2026-11-21 us-gas-price-on-november-22-2026
chk 2026-11-30 us-gas-price-on-december-1-2026
chk 2026-12-31 us-gas-price-on-january-1-2027
echo "$ok of $n tests pass"; [ "$ok" = "$n" ]
