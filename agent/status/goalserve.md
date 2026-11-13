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

## 1-hour figure + payload store — 13 Nov 15:17Z (P5, APPROVALS 18 / inbox #300)

- **1-hour hash-capture figure (14:04:31Z-15:04:31Z, the window the note asks for):**
  1,971 esports polls in the window (1,862 with `changed=true`), 2,236,840 B of log line
  bytes for the whole file in that window -> **53.7 MB/day** projection for the hash/size
  log (consistent with the earlier 52.5 MB/day one-minute figure).
  Esports response bodies totalled **269.4 MB in the hour** (network only; NOT stored
  before 15:09Z — the capture records recv_ns/sha1/bytes/changed only).
- **Changed-payload store (Nick yes 14:43:42Z, inbox #300): APPLIED 15:08:45Z, live 15:09:35Z.**
  Revert copy `live/goalserve/capture.py.pre-esports-payloads-20261113T150845Z`
  (sha256 `52068242107afaf7…` = the pre-edit file), `py_compile` OK, diff = +30/-1 lines
  (adds `store_payload()`, esports-only, gzip per UTC hour, 15 GB auto-stop).
  Restart gap 15:09:28Z -> first new row 15:09:35Z (7 s); hash capture kept running.
- **Measured over 7.6 min (15:09:35-15:17:08Z): 240 payload rows, 1,464,685 B gzipped ->
  279 MB/day gzipped** (raw bodies 23.2 MB in the same span -> ~17:1 gzip).
  Raw would be ~6.5 GB/day uncompressed; only the gzipped form is written.
- **CRITICAL (measured, please rule): `/vol2` is NOT a mounted volume on this box.**
  `findmnt -T /vol2` -> `/dev/sda1` mounted on `/` (root), `ls -ld /vol2` is a plain
  directory; root free = 17,564,192,768 B (55%). The real 98 GB data disk is mounted at
  `/mnt/HC_Volume_107257520` (69 GB free). So both this payload store and the pandascore
  capture write to ROOT, against charter clause 2 ("PK arbs data never on root"). At
  279 MB/day the payload store alone consumes the 2.56 GB between root free and the 15 GB
  floor in ~9 days; root also carries every other writer. Nothing moved — path is exactly
  what inbox #300 named. Options for IT: (a) point `PAYDIR` at the 98 GB disk and re-run,
  (b) mount the 98 GB disk at `/vol2`, (c) accept root with the existing 15 GB auto-stop.
  The store stops itself at the floor either way (`esports_payloads_STOP.log`).
- Free space at every step above the floor; no stop line written.

## Dota 2 coverage 16:15Z (inbox #304; posted 16:10Z, within the 16:15Z deadline — counts are bounded to the windows named below)

Method: read-only parse of the stored payloads `/vol2/goalserve/esports_payloads/esports_2026111315.jsonl.gz` +
`esports_2026111316.jsonl.gz` and the hash/size log `/vol2/goalserve/goalserve_20261113.jsonl`; PM markets from the
public gamma search API. Script `/root/_dota_counts.py`, raw output `/root/_dota_counts_out.json`.

1. **Dota 2 matches in `inplay-esports.gz`: bodies exist only from 15:09:30Z (the payload store start), so the
   match count below covers 15:09:30Z-16:08:06Z. For 14:04:31-15:09:35Z no bodies were stored (hash/size/changed
   only) — that window cannot be counted by match; it holds 2,135 esports polls, 2,015 with `changed=true`
   (14:04:31Z-16:05:33Z total: 3,957 polls / 3,757 changed; post-store 15:09:35Z+: 1,822 / 1,742).**
   3 distinct Dota 2 matches in the stored bodies, all with a Polymarket Game-N-Winner market (matched by team names):
   - `141165675` **PARIVISION vs Yellow Submarine** (DOTA2 - 1win Essence) 15:09:30Z-15:51:01Z, 1,299 stored
     payloads — PM: "Game 1 Winner" (closed, 1/0), "Game 2 Winner" (active), plus the BO3 "Match Winner" market
     on the 1win Essence / PGL Wallachia events.
   - `141165637` **Froglings vs PuckChamp** (DOTA2 - DreamLeague Div 2) 15:09:30Z-16:08:06Z, 1,821 payloads —
     PM: "Game 1 Winner" (0.9995) and "Game 2 Winner" (0.93) active.
   - `141165682` **Team Liquid vs LGD Gaming** (DOTA2 - 1win Essence) 16:00:03Z-16:08:06Z, 237 payloads —
     PM: "Game 1 Winner" (0.625), "Game 2 Winner" (0.605) and "Match Winner" active.
2. **bet365 odds-move events (stored payloads only; an "odds move" = two consecutive stored payloads whose event
   odds block differs, i.e. any participant `value_eu` or `suspend` change):** total 474 across the 3 matches —
   **PARIVISION vs Yellow Submarine 221, Froglings vs PuckChamp 253, Team Liquid vs LGD Gaming 0** (joined 16:00:03Z,
   odds block unchanged in its first 8 min, consistent with a pre-match/suspended line). No content before 15:09:35Z
   exists, so odds moves for 14:04-15:09Z are not measurable and are not claimed.
3. **ESTIMATE (not a projection fit): at the observed rate of 3 distinct in-play Dota matches in 59 min of body
   coverage, and 2-3 priced PM markets per BO3 (Game 1/Game 2/Match Winner), ~10 distinct matches and ~30 priced
   Dota events are reached in roughly 3-4 h of continued slate — i.e. on today's session if the current slate holds
   (assumptions: the ~1/s poll keeps returning the same in-play-only feed, every in-play Dota match gets a PM
   listing as all 3/3 did here, and evening leagues keep running). BLAST Slam from 17 Nov is the tier-1 slate that
   should deliver 10 distinct PM-listed matches on its own; treat 13-15 Nov as the thin pre-tournament window.
   Rate rests on 59 minutes of observation — thin.**

**Payload parse check (still owed):** a stored payload parses cleanly and shows team names — `info.name`
("PARIVISION vs Yellow Submarine") and `team_info.home/away.name`; per-game stat snapshots are present under `stats`
(`kills`, `towers`, `roshans`, `barracks`, `gold_def`, `res`). **Verdict wording: Goalserve has no Dota game events —
no timestamped kills/towers event stream at all, only per-poll stat counters plus bet365 odds. Never an edge until
it passes the locked test.** No round field exists in this feed. 145.1 MB of raw body across 1,745 stored payloads
(15:09:30Z-16:05:34Z); hour-15 gz 8.8 MB, hour-16 1.06 MB at 16:04Z.

**Disk (P7): the store still writes to root** — `/vol2` is a plain directory on the root volume (260 MB used there
at 16:2xZ), not a mount. The off-root move is filed as class 4 in `dialogue/APPROVALS.md` (open approval #20,
(filed 16:10Z): repoint `PAYDIR` + `OUT` to `/mnt/HC_Volume_107257520/pkarbs/goalserve/` (70 GB free), move, restart,
delete root copies only after row counts match. Root free 17.56 GB (above the 15 GB floor) and the store self-stops
at the floor, so waiting for the daily approval loses nothing. Revert: restore the pre-edit capture copy and point
the paths back.

## P3 closed - WebSocket token verified end to end, 13 Nov 16:33Z (OPEN row P3)

Measured this session on Prime; no code, config or unit was changed.

- **WS token: yes.** `POST .../api/v1/auth/gettoken` with `{"apiKey": KEY}` -> HTTP 200,
  181 B, `token` field present (169 chars), re-run 16:21Z and 16:33Z. `{"key": KEY}` ->
  400 `API key is missing or malformed.`
- **Cause of the earlier 400, one line: the JSON field name** (`key` rejected,
  `apiKey` accepted) - not the missing login.
- **Socket proof:** `wss://live.goalserve.com/ws/tennis?tkn=<token>` -> 5 messages, all
  `mt:"updt"`, in 0.6 s; `wss://live.goalserve.com/ws/esports?tkn=<token>` -> 5
  `mt:"updt"` in 4.9 s, no auth error, no close code. (Vendor facts in the v2 task say
  the WS has no esports channel; measured here it answers - recorded as measured.)
- **Login:** `GOALSERVE_USER` was already in the Goalserve env file (mode 600, written
  13 Nov 02:37Z; lengths only - user 12 chars, key 32 chars; value never printed, logged
  or committed), so no env edit was needed and the "login in no session" branch of P3
  does not apply.
- Replies filed this push: `agent/outbox/TO-IT-goalserve-missing-login-2026-11-12.md`,
  `agent/outbox/TO-IT-goalserve-key-pending-2026-11-12.md`.
