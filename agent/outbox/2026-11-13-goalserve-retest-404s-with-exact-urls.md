# Reply: Goalserve 404 retest with exact URLs (run 2026-11-13 13:09-13:19Z, Prime)

Full per-request table (URL with [R] secrets, HTTP status, bytes after gunzip, first 200
chars, auth sent): `agent/status/goalserve-probe.md`. No key, login or IP in any pushed
file (clause 13).

- **inplay-esports.gz: 200 WITH DATA** (98,339 B, 4 live events incl. cs2/dota at
  13:18Z; also 200 with NO credentials). The prior "404/empty" was never measured
  against this URL — `capture.py` never requests it. LoL final 14 Nov: feed is live now.
- **inplay-basket.gz: 200 WITH DATA** (133,718 B, 7 events) — "basketball 404" was wrong,
  the correct file name is `basket` and it works. **inplay-volleyball.gz: 200 WITH DATA**
  (115,908 B, 4 events). **inplay-amfootball.gz: 200 EMPTY** (`events:{}`, 102 B) — empty
  now, not a 404.
- **inplay-tennis.gz control: my probe got 429** (the running capture polls it at 1/s);
  the capture's own log proves it works — newest row 13:23:47Z, tennis 845,908 B
  changed=true, no errors.
- **inplay-cricket.gz: 404, expected** per the note (docs list no cricket inplay odds
  file) — not a failure.
- **Cricket livescore REST:** path `cricket/livescore` (as TASK-goalserve-v2 names it)
  returns **400 with an empty body on livescore.goalserve.com for every variant** (with
  creds, `&format=json`, `&date=`, trailing slash, `/cricket/home`, root, plain http),
  and **404 on inplay. and live. hosts**; scores. host does not resolve. Blocked on the
  exact URL from the Goalserve cricket documentation Nick received — it is not in this
  repo. Paste the URL path from those docs and this runs in minutes.
- **WebSocket token: WORKS.** POST `live.goalserve.com/api/v1/auth/gettoken`,
  `Content-Type: application/json`, body `{"apiKey": KEY}` → **HTTP 200, 181 B, returns a
  token** (also 200 for `{"user","apiKey"}`). `{"key": KEY}` → 400 "API key is missing or
  malformed". So the 02:19Z "works (JSON body)" claim is TRUE and the 02:37Z "400 in every
  mapping" is FALSE as written; **cause of the historical 400 = the JSON field name, not
  the missing login** (GOALSERVE_USER is present in `/etc/pkarbs/goalserve.env`, 600).
- **Esports capture NOT started** (step 3): a new collector is class 4 under charter
  clauses 5/15 (no measured 1-h MB/day trial, no writers.conf row, no pause hook, no box
  folder, no end date). Filed as APPROVALS.md item **#13** with the exact change and
  revert; tmux `goalserve` left untouched — nothing to revert today.
- **Massive and RapidAPI keys: YES, both reached Prime** — `/root/API_KEYS/massive/.env`
  (MASSIVE_API_KEY) and `/root/API_KEYS/rapidapi/.env` (RAPIDAPI_*) exist on the box
  (names only checked; values never read or printed).
- GitHub issue comments not possible from this box (`gh` not installed) — this file and
  `agent/inbox/IT-REPLY-goalserve-retest-2026-11-13.md` are the reply channel.

Count: notes run 1 (retest), outstanding 0 for this note, PENDING open 1 (APPROVALS #13).
