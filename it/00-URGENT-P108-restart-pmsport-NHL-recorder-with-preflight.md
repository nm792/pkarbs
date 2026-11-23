# P108: restart the NHL book recorder (pmsport) on the FIXED code, R-058 pre-flight first

State: pmsport books.jsonl.gz last written 20 Nov 14:28Z; no one has an order that stopped it, so it is NOT dead-by-design: UNKNOWN cause (likely stopped with the 20 Nov disk-floor event; recorder.log on Prime will say, paste its last 5 lines). The NHL cell of the v3 spec needs it.
Code: it/pm_sport_books.js on branch reviewer, commit f5be71e7f3, SHA-256 d9e92c9ac651ab63a7a2a0c631b9d12c932a4b65ad2ab17c908dfafb56fe3b2d. Default league is nhl. Never connects with 0 tokens (exit 4 after 120 s with no market), pidfile lock (second copy exit 2).
Tests (copy next to the script; each must print PASS): node test_pm_sport_books.js (12), node test_pm_sport_books_live.js (8).
Steps (Prime). V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmsport
1. Fetch it/pm_sport_books.js + both tests; sha256sum matches d9e92c9ac651ab63a7a2a0c631b9d12c932a4b65ad2ab17c908dfafb56fe3b2d; both tests PASS; else stop and paste.
2. pgrep -af pm_sport_books.js (paste). tail -5 $D/recorder.log (paste: says why it stopped). Do NOT start if another copy runs.
3. Pre-flight in a SEPARATE dir: node pm_sport_books.js $D/preflight-$(date -u +%H%M) '' 10 nhl preflight 60; echo exit=$?   Required: exit=0, JSON preflight PASS, ws_tokens = expected_tokens > 0, rows_written > 0. Exit 5 or 4 = nothing starts; paste the JSON. (No NHL games in the -8h..+36h window also gives exit 4: say so, not a fault.)
4. Only on PASS: cd $D; nohup node pm_sport_books.js $D 2026-12-31T00:00:00Z 10 nhl >> stdout.log 2>&1 &
5. 15 min later: python3 -I health_read.py ws $D --minutes 15 --pid-pattern pm_sport_books (health_read.py SHA in P107). Paste the HEALTH VERDICT line and pgrep showing one pid.
