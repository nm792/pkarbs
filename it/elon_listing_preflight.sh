#!/bin/bash
# Preflight for the Elon 48h listing recorder (pipeline/forward/elon_listing.py). Read-only. Prints PASS/FAIL per line with evidence. Run at T-30 min before every listing and paste the whole output.
# Overrides for tests only: V, REPO, OUT, HOURLY, NOW.
V=${V:-/mnt/HC_Volume_107257520}; REPO=${REPO:-$V/pkarbs}; OUT=${OUT:-$V/elon-listing}; HOURLY=${HOURLY:-$OUT/hourly.json}; NOW=${NOW:-$(date +%s)}; FAILS=0
say() { echo "$1 $2"; [ "$1" = FAIL ] && FAILS=$((FAILS+1)); return 0; }
echo "preflight $(date -u -d @$NOW +%FT%TZ)"
AV=$(df -B1 --output=avail "$V" 2>/dev/null | tail -1); [ "${AV:-0}" -gt 17000000000 ] && say PASS "disk free $AV bytes (>17 GB)" || say FAIL "disk free ${AV:-unknown} (<=17 GB)"
[ "$(timedatectl show -p NTPSynchronized --value 2>/dev/null)" = yes ] && say PASS "clock NTP-synchronised" || say FAIL "clock not NTP-synchronised (listing detection is to the second)"
code() { curl -s -m 15 -o /dev/null -w '%{http_code}' "$1"; }
[ "$(code 'https://gamma-api.polymarket.com/events/keyset?closed=false&limit=1&series_slug=elon-tweets-48h')" = 200 ] && say PASS "gamma reachable" || say FAIL "gamma unreachable"
[ "$(code 'https://clob.polymarket.com/time')" = 200 ] && say PASS "clob reachable" || say FAIL "clob unreachable"
[ "$(code 'https://data-api.polymarket.com/v2/trades?limit=1')" = 200 ] && say PASS "data-api reachable" || say FAIL "data-api unreachable"
XC=$(code 'https://xtracker.polymarket.com/api/users/elonmusk/trackings'); [ "$XC" = 200 ] && say PASS "xtracker reachable" || say FAIL "xtracker HTTP $XC: counts file cannot refresh on this host (fallback: the thread commits pipeline/forward/data/elon_hourly.json)"
if [ -f "$HOURLY" ]; then A=$(( (NOW - $(stat -c %Y "$HOURLY")) / 3600 )); LAST=$(python3 - "$HOURLY" "$NOW" <<'P'
import json,sys,datetime as dt
h=json.load(open(sys.argv[1]));k=max(h);t=dt.datetime.fromisoformat(k.replace("Z","+00:00")).timestamp();print(round((float(sys.argv[2])-t)/86400,2))
P
); python3 -c "import sys;sys.exit(0 if float('$LAST')<=2.0 else 1)" && say PASS "hourly counts newest hour is $LAST days old (<=2; the rule needs <=3 at listing)" || say FAIL "hourly counts newest hour is $LAST days old (>2)"; else say FAIL "hourly counts file $HOURLY missing"; fi
P=$(pgrep -f 'elon_listing.py record' | head -1); [ -n "$P" ] && say PASS "recorder pid $P alive" || say FAIL "recorder not running"
systemctl is-enabled elon-listing.service >/dev/null 2>&1 && say PASS "elon-listing.service enabled" || say FAIL "elon-listing.service not enabled"
S=$(cat "$OUT/seen.json" 2>/dev/null | head -c 200); [ -n "$S" ] && say PASS "seen.json present: $S" || say FAIL "seen.json missing"
( cd "$REPO" && python3 -m pytest -q pipeline/tests/test_elon_listing.py 2>&1 | tail -1 ) | grep -q passed && say PASS "unit tests pass" || say FAIL "unit tests failed or repo path wrong ($REPO)"
echo "repo sha $(cd "$REPO" 2>/dev/null && git rev-parse --short HEAD) ; recorder file sha256 $(sha256sum "$REPO/pipeline/forward/elon_listing.py" 2>/dev/null | cut -c1-16)"
[ "$FAILS" -eq 0 ] && echo "VERDICT ALL PASS (live read at $(date -u -d @$NOW +%H:%MZ))" || echo "VERDICT $FAILS FAIL: everything not PASS is UNVERIFIED"
