#!/bin/bash
# Preflight for the late-resolving-series book recorder (pipeline/forward/late_books.py). Read-only. PASS/FAIL per line. Run at T-30 min before each window in it/SCHEDULE-late-books-*.md and paste everything.
# Overrides for tests only: V, REPO, OUT, NOW.
V=${V:-/mnt/HC_Volume_107257520}; REPO=${REPO:-$V/pkarbs}; OUT=${OUT:-$V/late-books}; NOW=${NOW:-$(date +%s)}; FAILS=0
say() { echo "$1 $2"; [ "$1" = FAIL ] && FAILS=$((FAILS+1)); return 0; }
echo "preflight $(date -u -d @$NOW +%FT%TZ)"
AV=$(df -B1 --output=avail "$V" 2>/dev/null | tail -1); [ "${AV:-0}" -gt 17000000000 ] && say PASS "disk free $AV bytes (>17 GB)" || say FAIL "disk free ${AV:-unknown} (<=17 GB)"
[ "$(timedatectl show -p NTPSynchronized --value 2>/dev/null)" = yes ] && say PASS "clock NTP-synchronised" || say FAIL "clock not NTP-synchronised"
code() { curl -s -m 15 -o /dev/null -w '%{http_code}' "$1"; }
[ "$(code 'https://gamma-api.polymarket.com/events/keyset?closed=false&limit=1&series_slug=box-office-openings')" = 200 ] && say PASS "gamma reachable" || say FAIL "gamma unreachable"
[ "$(code 'https://clob.polymarket.com/time')" = 200 ] && say PASS "clob reachable" || say FAIL "clob unreachable"
P=$(pgrep -f 'late_books.py record' | head -1); [ -n "$P" ] && say PASS "recorder pid $P alive" || say FAIL "recorder not running"
systemctl is-enabled late-books.service >/dev/null 2>&1 && say PASS "late-books.service enabled" || say FAIL "late-books.service not enabled"
[ -s "$REPO/it/late_books_series.txt" ] && say PASS "series list $(grep -vc '^#' "$REPO/it/late_books_series.txt") lines" || say FAIL "series list missing"
( cd "$REPO" && python3 -m pytest -q pipeline/tests/test_late_books.py 2>&1 | tail -1 ) | grep -q passed && say PASS "unit tests pass" || say FAIL "unit tests failed or repo path wrong ($REPO)"
echo "repo sha $(cd "$REPO" 2>/dev/null && git rev-parse --short HEAD) ; recorder file sha256 $(sha256sum "$REPO/pipeline/forward/late_books.py" 2>/dev/null | cut -c1-16)"
[ "$FAILS" -eq 0 ] && echo "VERDICT ALL PASS" || echo "VERDICT $FAILS FAIL: everything not PASS is UNVERIFIED"
