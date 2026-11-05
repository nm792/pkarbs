# status — oddspapi-hist (OddsPapi historical odds pull, 4-5 Nov)
State: DONE
Start: 2026-11-05 02:15:56Z
End:   2026-11-05 02:16:57Z (ran to completion, ~60s)
hist_ok: 4  (fixtures: 10, live-or-done-with-odds found in window, 6/10 returned "No historical odds found")
RESULT: **FAIL** (pass bar: hist_ok>=20, >=10 tennis, >=1 CS2/LoL)
- Fixture universe in window was small: only 10 fixtures across tennis/CS2/LoL/Dota had odds+status in the 4-5 Nov window.
- Data WAS committed (tarball at rn1/scores/oddspapi/2026-11-04/) for the thread to inspect.
- Not retried: same window would return the same small fixture set; widened window is the thread's call.
Left-running: cricket-feeds (books growing), NBA capture, cs2-ws-logger unaffected.
