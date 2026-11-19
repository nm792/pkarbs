#!/bin/bash
# Live preflight for the Goalserve / CS2 / Dota pipeline (Goalserve thread, 19 Nov 2026). Read-only, no credentials, prints PASS/FAIL per line with evidence.
# Run at T-30 min before every window. Anything not PASS here is UNVERIFIED. Overrides for tests only: V, PIDS_FN, NOW.
V=${V:-/mnt/HC_Volume_107257520}; NOW=${NOW:-$(date +%s)}; FAILS=0
G=$V/pkarbs/goalserve; MAXAGE=${MAXAGE:-900}
say() { echo "$1 $2"; if [ "$1" = FAIL ]; then FAILS=$((FAILS+1)); fi; return 0; }
age_of() { local m; m=$(stat -c %Y "$1" 2>/dev/null) || { echo 999999; return; }; echo $((NOW - m)); }
newest() { ls -1t "$1"/* 2>/dev/null | head -1; }
echo "preflight $(date -u -d @$NOW +%FT%TZ)"
AV=$(df -B1 --output=avail "$V" 2>/dev/null | tail -1); [ "${AV:-0}" -gt 17000000000 ] && say PASS "disk free $AV bytes (>17 GB)" || say FAIL "disk free ${AV:-unknown} bytes (<=17 GB)"
if [ -n "${PIDS_FN:-}" ]; then P=$($PIDS_FN capture); else P=$(pgrep -f 'live/goalserve/capture.py' | head -1); fi
[ -n "$P" ] && say PASS "goalserve capture pid $P alive" || say FAIL "goalserve capture not running"
for s in esports tennis hockey_nhl basketball; do
  f=$(newest "$G/${s}_payloads"); a=$(age_of "${f:-/nonexistent}"); sz=$(stat -c %s "${f:-/nonexistent}" 2>/dev/null || echo 0)
  [ "$a" -le "$MAXAGE" ] && say PASS "$s newest hour file $(basename "${f:-none}") age ${a}s size ${sz}" || say FAIL "$s newest hour file $(basename "${f:-none}") age ${a}s (>${MAXAGE}s) size ${sz}"
  ls "$G/${s}_payloads"/*STOP.log >/dev/null 2>&1 && say FAIL "$s STOP.log exists: $(tail -c 200 "$G/${s}_payloads"/*STOP.log 2>/dev/null | tr '\n' ' ')"
done
for s in esports tennis hockey_nhl basketball; do ls "$G"/${s}_payloads_STOP.log >/dev/null 2>&1 && say FAIL "$s STOP log: $(tail -c 200 "$G/${s}_payloads_STOP.log" | tr '\n' ' ')"; done
PMF=$(newest "$V/pkarbs/thesports/final-topics-32295b"); a=$(age_of "${PMF:-/nonexistent}"); [ "$a" -le "$MAXAGE" ] && say PASS "polymarket recorder newest file $(basename "${PMF:-none}") age ${a}s" || say FAIL "polymarket recorder newest file age ${a}s"
a=$(age_of "$V/pkarbs/pmcs2/books.jsonl"); [ "$a" -le "$MAXAGE" ] && say PASS "pmcs2 books.jsonl age ${a}s" || say FAIL "pmcs2 books.jsonl age ${a}s (CS2 book recorder not writing)"
if [ -n "${PIDS_FN:-}" ]; then P=$($PIDS_FN pmcs2); else P=$(pgrep -f 'pm_cs2_books.js' | head -1); fi
[ -n "$P" ] && say PASS "pmcs2 recorder pid $P alive" || say FAIL "pmcs2 recorder (pm_cs2_books.js) not running"
DF=$(find "$V/pkarbs/pmdota" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-); a=$(age_of "${DF:-/nonexistent}"); [ "$a" -le "$MAXAGE" ] && say PASS "dota PM recorder (pkarbs/pmdota) newest file $(basename "${DF:-none}") age ${a}s" || say FAIL "dota PM recorder (pkarbs/pmdota) newest file age ${a}s (only a FAIL while a Dota game is in window; the full check is feeds/check_pmdota.sh)"
${CRON_FN:-crontab -l} 2>/dev/null | grep -q daily_look_cron && say PASS "daily look cron installed" || say FAIL "daily look cron NOT installed"
[ "$FAILS" -eq 0 ] && echo "VERDICT ALL PASS (live read at $(date -u -d @$NOW +%H:%MZ))" || echo "VERDICT $FAILS FAIL: everything not PASS is UNVERIFIED"
