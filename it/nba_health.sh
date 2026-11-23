#!/bin/bash
# R-037/R-058 HEALTH READ for pm_sport_books.js (NBA/NHL/tennis). Usage: bash nba_health.sh <outDir> [wait_s=60]   Exit 0 = PASS, 1 = FAIL. Read-only.
OUT="$1"; W="${2:-60}"; F=0; say() { echo "$*"; }
P=$(cat "$OUT/recorder.pid" 2>/dev/null); ALIVE=no
if [ -n "$P" ] && kill -0 "$P" 2>/dev/null && tr '\0' ' ' < "/proc/$P/cmdline" 2>/dev/null | grep -q pm_sport_books; then ALIVE=yes; fi
N=$(pgrep -fc 'pm_sport_books\.js' || true)
[ "$ALIVE" = yes ] || { F=1; say "FAIL pid: recorder.pid ($P) is not a live pm_sport_books process"; }
[ "$N" = 1 ] || { F=1; say "FAIL writers: $N pm_sport_books processes (must be exactly 1)"; }
TOK=$(grep -o 'ws open, tokens [0-9]*' "$OUT/recorder.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
[ "${TOK:-0}" -gt 0 ] 2>/dev/null || { F=1; say "FAIL tokens: last 'ws open' line says tokens '${TOK:-none}' (must be > 0)"; }
M=$(wc -l < "$OUT/markets.jsonl" 2>/dev/null || echo 0)
[ "${TOK:-0}" = "$((M*2))" ] || say "NOTE tokens ${TOK:-0} vs 2 x markets $((M*2)) (new games may have joined by subscribe; not a FAIL)"
S1=$(stat -c %s "$OUT/books.jsonl.gz" 2>/dev/null || echo 0); sleep "$W"; S2=$(stat -c %s "$OUT/books.jsonl.gz" 2>/dev/null || echo 0)
GAMES=$(grep -c '^' "$OUT/markets.jsonl" 2>/dev/null || echo 0)
[ "$S2" -gt "$S1" ] || { F=1; say "FAIL growth: books.jsonl.gz $S1 -> $S2 bytes in ${W}s (no growth; only valid while a game is live)"; }
E=$(grep -ciE 'error|FATAL|REFUSED' "$OUT/recorder.log" 2>/dev/null); E=${E:-0}
[ "$E" = 0 ] || say "NOTE errors/FATAL/REFUSED lines in recorder.log: $E (read them; ws error lines before a clean 'ws open' are reconnects)"
FREE=$(df -P --output=avail -B1G "$OUT" 2>/dev/null | tail -1 | tr -d ' ')
say "pid=$P alive=$ALIVE writers=$N tokens=${TOK:-0} markets=$M gz_bytes=$S1->$S2 (${W}s) disk_free_GB=$FREE price_source=each row asset = that token's OWN book (bids/asks), YES/NO never derived"
[ $F = 0 ] && say "HEALTH PASS" || say "HEALTH FAIL: stop, keep files, fix, restart, new read within 15 min"; exit $F
