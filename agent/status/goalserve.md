# status: Goalserve trial — capture RUNNING (Part A), 4 sports; 404 claims CORRECTED

Updated: 13 Nov 2026 13:25Z UTC (probe run 13:09-13:19Z; this file's earlier 404 lines
are corrected in place — see "Corrections 13:25Z")

- **Env file:** `/etc/pkarbs/goalserve.env` — mode 600, GOALSERVE_USER + GOALSERVE_KEY (never printed/committed).
- **Egress-IP whitelist: yes** (prior check + IT).
- **Auth:** user+key authenticated — `inplay-tennis.gz?user&key` HTTP 200 (~221 ms).
- **GET TOKEN (`live.goalserve.com/api/v1/auth/gettoken`):** **WORKS — HTTP 200 with JSON
  body `{"apiKey": KEY}`** (181 B, returns a token; `{"user","apiKey"}` also 200).
  The earlier "400 in every field mapping" was the wrong field name: `{"key": KEY}` is the
  only mapping tested that returns 400 ("API key is missing or malformed"). Full forms in
  `agent/status/goalserve-probe.md`.
- **Capture:** RUNNING, tmux `goalserve`, `live/goalserve/capture.py`, log
  `/vol2/goalserve/goalserve_YYYYMMDD.jsonl` (recv_ns, sha1, change first-seen per poll).
  Newest row 13:23:47Z, no errors, 22.1 MB today.
  - Polling (verified OK): **tennis, soccer, baseball, hockey (NHL)**.
- Started 02:38Z 13 Nov; ~1 poll/s, error-safe (429/404 logged and skipped).

## Corrections 13:25Z (13 Nov, probe `goalserve-probe.md`)

- ~~basketball (404), esports Lol/CS2/Dota2 (404/empty) not available~~ — **WRONG.**
  Measured 13:09-13:18Z: `inplay-basket.gz` 200 (133,718 B, 7 events),
  `inplay-esports.gz` 200 (98,339 B, 4 live events incl. cs2/dota; also 200 without
  creds), `inplay-volleyball.gz` 200 (115,908 B, 4 events). The earlier 404s were never
  measured against these URLs — `capture.py` does not request them (its SPORTS dict has
  only tennis/soccer/baseball/hockey).
- `inplay-amfootball.gz` = 200 with an EMPTY `events:{}` (102 B) — empty-now, not 404.
- `inplay-cricket.gz` = 404, expected per the note (no cricket inplay file; not a failure).
- Cricket livescore path `cricket/livescore`: 400 (empty) on livescore.host for every
  variant tried, 404 on inplay./live. hosts — blocked on the exact URL from the vendor
  docs (asked in the inbox reply).
- **Esports capture: STARTED 2026-11-13 14:04:31Z** (Nick "yes" 13:46Z, APPROVALS item 18;
  correction 14:10Z — the "NOT started / class 4" line below this one is history). See
  `agent/outbox/2026-11-13-goalserve-esports-capture-APPROVED.md` for the full report.

Next: bind the PM/CLOB + TheSports recorders for the matching markets (Part A alignment);
esports RUNNING since 14:04:31Z (APPROVALS item 18 applied; 1-hour MB/day due 15:04:31Z); cricket livescore still blocked on the docs URL.

## Esports started — 13 Nov 14:10Z (APPROVALS item 18, Nick yes 13:46Z)

- **Capture started: yes.** Start 2026-11-13 14:04:31Z; gap from kill to first new row
  4.7 s (row `2026-11-13T14:04:35.188+00:00`).
- Change: one line `"esports": "/inplay-esports.gz",` in `live/goalserve/capture.py`,
  sha256 `52068242107afaf762a6f72a53d298eee1fd23bab925d6c8413f31f231d51204`;
  revert copy `capture.py.pre-esports-20261113T140357Z` (sha `a9751804…`). `py_compile` OK.
  Poll left at 1.0 s (approved single-line scope; 0.5 s is a separate edit).
- writers.conf row: `goalserve|/vol2/goalserve|pkarbs/goalserve|-|y|hourly`
  (backup `writers.conf.pre-goalserve-20261113T140908Z`). Box folder `pkarbs/goalserve`.
- Free space at start: 17 GB available (55%) — above the 15 GB floor, not stopped.
  The earlier "VOL2 ~94%" figure was stale; measured 14:09Z.
- Rows: 32/32 new rows carry an esports payload, 0 errors. Stored cost measured over
  14:05:32Z-14:06:32Z: +36,455 B / +32 rows -> 52.5 MB/day whole-file projection,
  ~40 MB/day before the restart, so ~+12 MB/day from esports. Payload not stored
  (recv_ns, sha1, bytes, changed, first_seen_ns only).
- **1-hour MB/day trial figure due 15:04:31Z — not yet measured.**
- Not in place, nothing invented: pause hook (no disk_gate/start_writer on disk for a
  tmux capture) and trial end date (not named in the goalserve task files). Reviewer to
  specify both.
