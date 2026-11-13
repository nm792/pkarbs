# status: Goalserve trial — key+login received; HTTP feed authenticated; gettoken still 400

Updated: 12 Nov 2026 ~21:3xZ UTC

- **Env file:** `/etc/pkarbs/goalserve.env` exists, mode 600, `GOALSERVE_KEY=…` (never printed/committed). `GOALSERVE_USER` NOT yet added — env update for the login awaits live-session approval (timed out).
- **Egress IP whitelist: yes** (prior check + IT, 433adfc1).
- **Hard check (a) inplay-tennis.gz:** yes — HTTP 200; and **authenticated poll works** with `user=emblematic07&key=…` → HTTP 200 (73,366 bytes). The trial's HTTP polling path is authenticated and usable.
- **Hard check (b) gettoken (`live.goalserve.com/api/v1/auth/gettoken`):** still **NO** — `400 "API key is missing or malformed"` for `user+key`, `login+password`, `user+password`, `username+password`. The WebSocket token endpoint does not accept the (user,key) pair in any standard mapping; appears to be a separate/unactivated path and is not required for the HTTP polling capture.
- **Next:** (1) approve the one-line env update adding `GOALSERVE_USER=emblematic07`; (2) stand up the Part A HTTP poller (TASK-goalserve-trial) on /vol2 logging recv ns / HTTP Date / sha1 / fields per poll.

Blocked on: env write for GOALSERVE_USER (approval timed out). Feed itself is usable.
