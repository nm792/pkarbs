# status: Goalserve 404 retest probe — run 2026-11-13 13:09-13:19Z (Prime, read-only)

Answers inbox `2026-11-13-goalserve-retest-404s-with-exact-urls.md` (PR #289) and
`TO-IT-goalserve-retest-first-2026-11-13-1255Z.md`. Method: exact paths from the note,
GET with `?user=[R]&key=[R]` exactly as `live/goalserve/capture.py` builds them (plus
no-cred variants), `Accept-Encoding: gzip`. user/key replaced by [R]; no server IP
recorded anywhere (clause 13). No capture process was changed by this probe.

Rate limit: the live capture polls `inplay-tennis.gz` at 1/s, so extra tennis probes
return 429. The tennis control is therefore taken from the capture's own log (row below).

| # | request | URL (secrets [R]) | auth sent | HTTP | bytes after gunzip | first 200 characters of body | 404 or empty 200? |
|---|---|---|---|---|---|---|---|
| 1 | GET inplay-esports.gz | https://inplay.goalserve.com/inplay-esports.gz?user=[R]&key=[R] | login+key query | 200 | 98,339 | `{"bm":"","updated":"11.13.2026 13:09:07","updated_ts":1794575347722,"events":{"141165669":{"core":{"safe":"","removed":` | **200 WITH DATA** |
| 2 | GET inplay-basket.gz | https://inplay.goalserve.com/inplay-basket.gz?user=[R]&key=[R] | login+key query | 200 | 133,718 | `{"bm":"","updated":"11.13.2026 13:09:06","updated_ts":1794575346144,"events":{"204480231":{"core":{"safe":"","removed":` | **200 WITH DATA** |
| 3 | GET inplay-volleyball.gz | https://inplay.goalserve.com/inplay-volleyball.gz?user=[R]&key=[R] | login+key query | 200 | 115,908 | `{"bm":"","updated":"11.13.2026 13:09:08","updated_ts":1794575348179,"events":{"204516485":{"core":{"safe":"","removed":` | **200 WITH DATA** |
| 4 | GET inplay-amfootball.gz | https://inplay.goalserve.com/inplay-amfootball.gz?user=[R]&key=[R] | login+key query | 200 | 102 | `{"bm":"","updated":"11.13.2026 13:09:07","updated_ts":1794575347035,"events":{}}` | **200 EMPTY** (no events now; not a 404) |
| 5 | GET inplay-tennis.gz | https://inplay.goalserve.com/inplay-tennis.gz?user=[R]&key=[R] | login+key query | 429 | 51 | `{ "status": "429", "message": "Too Many Requests" }` | neither — rate-limited (see control below) |
| 6 | GET inplay-esports.gz no creds | https://inplay.goalserve.com/inplay-esports.gz | none | 200 (retry 13:12:44Z; first try 429) | 97,010 | `{"bm":"","updated":"11.13.2026 13:12:44","updated_ts":1794575564312,"events":{"141165669":{"core":...` | **200 WITH DATA without creds** |
| 7 | GET inplay-tennis.gz no creds | https://inplay.goalserve.com/inplay-tennis.gz | none | 429 | 51 | `{ "status": "429", "message": "Too Many Requests" }` | neither — rate-limited |
| 8 | GET cricket livescore | https://livescore.goalserve.com/cricket/livescore?user=[R]&key=[R] | login+key query | 400 | 0 | (empty body) | neither — **400, host answers but refuses the request** |
| 9 | GET cricket livescore | https://inplay.goalserve.com/cricket/livescore?user=[R]&key=[R] | login+key query | 404 | 0 | (empty) | 404 |
| 10 | GET cricket livescore | https://live.goalserve.com/cricket/livescore?user=[R]&key=[R] | login+key query | 404 | 0 | (empty) | 404 |
| 11 | GET cricket livescore | https://scores.goalserve.com/cricket/livescore?user=[R]&key=[R] | login+key query | n/a | n/a | DNS: name not resolved | neither — host does not exist |
| 12 | GET inplay-cricket.gz | https://inplay.goalserve.com/inplay-cricket.gz?user=[R]&key=[R] | login+key query | 404 | 0 | (empty) | 404 — **expected per the note; not a failure** |

Tennis control (the note's known-good file): the RUNNING capture proves it —
`/vol2/goalserve/goalserve_20261113.jsonl` newest row 13:23:47Z, tennis 845,908 B
`changed=true`, soccer 1,427,778 B, baseball 102 B, hockey_nhl 53,617 B, no errors.

Livescore variants also tried on livescore.goalserve.com, all **400 with empty body**:
root `/`, `/cricket/home`, `/cricket/livescore?...&format=json`, `...&date=2026-11-13`,
trailing slash, and plain `http://`. The path `cricket/livescore` is the one named in
TASK-goalserve-v2 from the vendor docs; the exact URL from the docs Nick received is not
in this repo, so the working base host cannot be confirmed from here — blocked on the
docs URL (asked in the inbox reply).

## WebSocket token reconciliation (which earlier claim is true)

- **TRUE (02:19Z "WS token WORKS (JSON body)"):** POST https://live.goalserve.com/api/v1/auth/gettoken,
  `Content-Type: application/json`, body `{"apiKey":[R]}` → **HTTP 200, 181 bytes,
  `{"token":"<JWT redacted>"}`**. Same 200 for `{"user":[R],"apiKey":[R]}`.
- **FALSE as written (02:37Z "gettoken still 400 in every mapping"):** body `{"key":[R]}` →
  **HTTP 400, 150 bytes** `{"type":"https://tools.ietf.org/html/rfc9110#section-15.5.1",
  "title":"Authentication failed","status":400,"detail":"API key is missing or malformed."}`
- **Cause of the historical 400 in one line: the JSON field name** — `key` is rejected,
  `apiKey` is accepted. Not the missing login: `GOALSERVE_USER` is present in
  `/etc/pkarbs/goalserve.env` (mode 600) and gettoken does not require it.
- WS connect itself (`wss://live.goalserve.com/ws/<sport>?tkn=<token>`) not tested in this
  probe — the note asked only for the token request form and status.

## Event counts (13:18:35Z recheck, same URLs)

esports **4 live events** (payload contains cs2/dota), basket 7, volleyball 4,
amfootball 0. LoL Worlds final 14 Nov — the feed is live now.

## Not done (gated, not skipped)

- **Esports capture NOT started.** Starting it is class 4 under charter clauses 5/15
  (new collector / code change: no measured 1-hour MB/day trial, no writers.conf row, no
  pause hook, no box folder, no end date yet). Filed as APPROVALS.md item **#13** with the
  exact change; tmux `goalserve` capture left untouched (revert: none needed — nothing changed).
- Live capture unchanged: tmux `goalserve`, `live/goalserve/capture.py`, 4 sports, log
  `/vol2/goalserve/goalserve_20261113.jsonl` (22.1 MB today, newest row 13:23:47Z).
