# Reply: Goalserve install and go (12 Nov 2026)

- **Env installed:** `/etc/pkarbs/goalserve.env` (mode 600, `GOALSERVE_KEY=…`, never printed/committed).
- **Egress-IP whitelist check: yes** (inplay feed loads from this server).
- **Hard check (a) inplay-tennis.gz:** yes — HTTP 200 / 87,685 bytes without key (IP-whitelisted). With `?key=` → HTTP 429 (rate-limit/wrong param form).
- **Hard check (b) gettoken:** **NO** — `400 "API key is missing or malformed"`. Goalserve auth needs the account **username/login + key**; only the key arrived. Trial is HELD at the hard-check gate until the login is provided.
- Status: `agent/status/goalserve.md`. Escalated to IT (TO-IT) — missing login.
- Revert of key: delete `/etc/pkarbs/goalserve.env`.

Next action (once login provided): re-run gettoken, start TASK-goalserve-trial Part A capture on /vol2.
