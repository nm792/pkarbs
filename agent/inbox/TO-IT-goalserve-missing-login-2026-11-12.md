| UTC | from | problem | impact | agent answer + proof | IT ruling |
|---|---|---|---|---|---|
| 2026-11-12 21:12 | agent | Goalserve trial blocked at hard-check (b): key installed (/etc/pkarbs/goalserve.env, 600), egress whitelist OK, inplay-tennis.gz loads (200), but gettoken returns 400 "API key is missing or malformed" — Goalserve token auth needs the account username/login in addition to the key, and only the key was sent. | trial cannot start (token auth gate) | key installed; status agent/status/goalserve.md; need the Goalserve login/username to re-run gettoken and start Part A | |
