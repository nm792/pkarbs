# status: Goalserve trial — capture RUNNING (Part A started)

Updated: 12 Nov 2026 ~21:55Z UTC

- **Env file:** `/etc/pkarbs/goalserve.env` — mode 600, `GOALSERVE_USER=…`, `GOALSERVE_KEY=…` (never printed/committed).
- **Egress-IP whitelist: yes** (prior check + IT).
- **Auth:** HTTP polling authenticated with user+key — `inplay-tennis.gz?user&key` = HTTP 200 (verified 2×, 556 KB / 551 KB, poll ~221 ms).
- **gettoken (WebSocket token):** still 400 — separate/unactivated path; not needed for the HTTP polling capture.
- **Capture:** RUNNING — tmux session `goalserve`, `live/goalserve/capture.py`, logs `/vol2/goalserve/goalserve_YYYYMMDD.jsonl`. Per poll: recv_ns, HTTP Date(0), payload sha1, change first-seen. Polling tennis, cricket, soccer, basketball.
  - tennis: OK; soccer: OK; `inplay-cricket.gz` → **404** (cricket uses a different Goalserve endpoint — needs the correct URL); basketball: to confirm.
- **Next:** add the correct cricket endpoint (and the task's remaining sports: LoL, CS2, Dota 2, NHL); align PM/CLOB + TheSports recorders per Part A; run through the trial. SMOKE: first log row 2026-11-13T02:38Z.

Blocked on: correct Goalserve cricket endpoint (inplay-cricket.gz 404). Otherwise running.
