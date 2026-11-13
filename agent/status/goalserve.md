# status: Goalserve trial — WS token WORKS; 400 was request format, not missing login

Updated: 13 Nov 2026 ~02:2xZ UTC

- **Env file:** `/etc/pkarbs/goalserve.env` exists, mode 600, `GOALSERVE_KEY` present (32 chars). `GOALSERVE_USER` (emblematic07) is documented in TASK-goalserve-v2 and TO-IT; not required for gettoken.
- **Egress IP whitelist check:** yes — server public egress is the whitelisted IP (inplay feed loads).
- **Hard check (a)** `https://inplay.goalserve.com/inplay-tennis.gz`: yes (HTTP 200) — IP-whitelisted path; with `?key=` param form → 429.
- **Hard check (b) gettoken `POST https://live.goalserve.com/api/v1/auth/gettoken`:** **YES** — HTTP 200, valid JWT (3 parts, exp/uid/iat/nbf). The earlier 400 "API key is missing or malformed" was a **request-format** issue: the param/`?key=` form, not the missing login. The documented JSON body `{"apiKey": KEY}` (Content-Type: application/json) returns a token; login is not needed for token auth. Answering OPEN row P3: cause = request format, one line.
- **Next:** start TASK-goalserve-trial Part A capture (WS wss://live.goalserve.com/ws/{sport}?tkn={token}) per note; trial is 30 days, LoL Worlds final 14 Nov.

Blocked on: nothing (token works). Capture start per the note's trial flow.
