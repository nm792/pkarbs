# status: Goalserve trial — key installed; hard check (b) blocked on missing login

Updated: 12 Nov 2026 ~21:10Z UTC

- **Env file:** `/etc/pkarbs/goalserve.env` exists, mode 600, `GOALSERVE_KEY=…` (never printed/committed).
- **Egress IP whitelist check:** yes — the server's public egress is the whitelisted server IP (inplay feed loads).
- **Hard check (a)** `https://inplay.goalserve.com/inplay-tennis.gz`: **yes** (HTTP 200, 87,685 bytes) without the key (IP-whitelisted path). With `?key=…` → **429** (rate-limit/param form).
- **Hard check (b)** WebSocket token `POST https://live.goalserve.com/api/v1/auth/gettoken`: **NO** — `400 "API key is missing or malformed"`. Goalserve token auth needs the account **username/login in addition to the key**; only the key was received. This holds the full trial run per the note's hard-check gate.
- **Next:** once the Goalserve login/username is provided, re-run gettoken, then start TASK-goalserve-trial Part A capture.

Blocked on: missing Goalserve username/login (raised to IT / owner).
