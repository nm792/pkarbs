# tweetcount-recorder probe — 2026-11-10 ~05:21Z — PARTIAL PASS, needs a script guard (code change, class-4)

Ran per agent/inbox/2026-11-10-tweetcount-recorder.md step 1: `python3 agent/tasks/tweetcount-recorder.py --out /vol2/pkarbs/tweetcount --probe` (script on origin pnd99n; extracted to /root/pkarbs, py_compile OK).

MEASURED (this box, 05:20Z):
- xtracker.polymarket.com reachable and working: 6 open "Elon Musk # tweets" events listed with tracking ids; e.g. "Nov 3 - Nov 10" tracking total 272.
- clob.polymarket.com reachable: HTTP 200 on book for working tokens; gamma-api HTTP 200.
- BUT book() 404s for specific events' first-market tokens: "Nov 3 - Nov 10 2026" and "Nov 6 - Nov 13 2026" → `HTTP Error 404: Not Found` (from clob, not a network failure — other tokens 200 from the same box in the same run; per-event check: Nov9-11 200 (bids26/asks121), Nov12-14 200, Nov10-17 200, Nov13-20 200).

CONSEQUENCE: as written, the recorder dies at the first 404 (probe mode line 58, record mode line 81 both call book() unguarded), so starting it now would crash-loop within the first poll.

ASK FOR THE THREAD (this is the project channel): patch tweetcount-recorder.py to skip tokens whose book 404s (try/except around book(), or per-market fallback to the next market). That is a code edit → class-4 (CHANGE-BATCH) under the 09-08..11-15 gate; I have not patched it. Until the guard exists the recorder is not started; first decision T is 12 Nov 17:00Z, so there is time.

NOT started (no process, no crontab, no unit): avoiding a crash-loop. No orders, no keys used.
