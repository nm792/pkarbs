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
## P8 part 2 - gamma limit=50 APPLIED, PM market registration live again (13 Nov 17:06Z; OPEN row P8; IT reply eb3abacd ruled approval #21 Type A, clause 22A)

- **Change** (`live/thesports/capture.py`, `discover_pm()` only, 3 lines): `limit=100 -> 50`, page stride `range(0,1000,100) -> range(0,1000,50)`, and the companion break threshold `len(r) < 100 -> len(r) < 50`. The threshold is the ONE line beyond the filed spec: with only the two spec lines a full 50-row page reads `< 100`, so pagination stops after page 1 and the stride change does nothing past offset 0. The reviewer can strike it if unwanted. `py_compile` OK.
- **Backup / revert:** `live/thesports/capture.py.pre-limit50-20261113T170314Z`, sha256 `e277381c826c0ad43fe4a7bd1595a09f7615ab78990765d4130258c21f7b9c54` (byte-identical to the pre-edit blob). Revert = restore that copy, restart the unit.
- **Restart:** old `timeout 552000 python3 ... capture.py` (pids 2818604/2818605, up since 8 Nov 00:42Z) stopped; `thesports-capture-b.service` started **17:06:03Z**, MainPID 465179, `is-active` = active. Restart gap about 70 s.
- **200 discover line:** `log.jsonl` 17:06:10Z `{"what":"discover_pm","tokens":216,"new":216}` - success rows only (errors are separate `discover_pm_err` rows); the last `406 Not Acceptable` was 16:58:36Z.
- **Registration counter:** `markets.jsonl` 2,847 -> **3,161 rows** (+314) by 17:06:10Z - registration is moving again.
- **Other streams after the restart:** books newest 17:06:54Z, pmws 17:06:53Z, ts_mqtt 17:05:32Z - all live; no other stream was stale.
- **Not changed:** no other line of the file. The relaunch keeps the original `timeout 552000`, which expires 14 Nov about 09:06Z with no restart guard anywhere on the box (no cron or unit references capture.py) - flagged as one TO-IT line, not touched here.

## LoL final start — MEASURED 13 Nov 22:46Z (P9; inbox `2026-11-13-lol-final-start-time-and-recorder-timeout.md` item 1)

- **Worlds 2026 final scheduled start: 2026-11-14 19:00:00Z** (Saturday 14 Nov, Barclays Center, New York).
- Source: the official schedule call `esports-api.lolesports.com/persisted/gw/getSchedule`
  (`hl=en-US`, `leagueId=98767975604431411` = Worlds, the id from this repo's own
  `rn1/scores/lol/winmodel/list_games.py`), **HTTP 200, response fetched 2026-11-13T22:46:24Z**
  (request and body both inside that second).
- Event in the response: `blockName: "Finals"`, `state: "unstarted"`, match id `115660540726095133`,
  **Gen.G Esports vs BILIBILI GAMING** — the only Worlds event with `startTime >= 2026-11-12`
  among the 80 events read.
- Corroboration: `getEventDetails` for the same match id returned HTTP 200 at 2026-11-13T22:46:55Z
  with the same two teams; its event-level `startTime` is null, so the time above comes from
  `getSchedule` only.
- Label: **MEASURED** — read from the API response at the times above, not from memory or web search.
  This is the start time to plan the 14 Nov capture window against (it lands after the old
  09:06Z timeout, which is now gone — see below).

## P9 recorder confirmation — measured 13 Nov 22:48Z (inbox #311/#312 item 2; IT deadline 14 Nov 06:00Z)

Guard work was already pushed at `ae85a3d4c9` + `3fc673c556` (OPEN row P9 status); this is the
confirmation the note asks for.

- **No `timeout 552000` on the live path.** Unit text now (`thesports-capture-b.service`, transient
  systemd-run): `ExecStart="/usr/bin/python3" "-I" ".../live/thesports/capture.py" "<data-vol>/final-topics-32295b" "160" "--share" "<data-vol>/final-topics-32295b/share"`,
  `EnvironmentFile=/etc/pkarbs/thesports.env`, **no timeout line anywhere in the unit**; capture.py
  bounds itself at 160 h. The guard's relaunch line carries no `timeout` either (`live/thesports/guard_capture_b.sh`).
- **Restart guard:** `*/5 * * * * bash /root/pkarbs/live/thesports/guard_capture_b.sh >> /var/log/thesports_capture_guard.log`
  (flock-guarded). Rule (v2, IT 18:10Z): process absent OR newest row older than 600 s across
  books/pmws/ts_mqtt/log → TERM capture pids + relaunch with the env file (ts_poll excluded:
  written only on body change); every restart logged. Guard ticks `rc=0` through **22:45:01Z**;
  live process **pid 898340, started by the guard at 18:16:51Z** (4 h 31 m up at 22:48Z), relaunch
  proven live 18:16:51Z with `creds:true` (`ae85a3d4c9`), STALE branch dry-run tested with
  `GUARD_MAX_AGE=-1` (`3fc673c556`).
- **Revert:** restore the pre-guard crontab backup `crontab.pre-p9-guard-20261113T1818Z.txt` and
  `rm /root/pkarbs/live/thesports/guard_capture_b.sh`.
- **Newest row UTC per stream** (data volume, measured 22:48:04Z):

| stream | file | newest row UTC | age at 22:48:04Z |
|---|---|---|---|
| PM market registration | `markets.jsonl` | 2026-11-13 22:44:09.169Z | 4 min (live again since the P8 `limit=50` fix) |
| CLOB books (1 s) | `books.jsonl` | 2026-11-13 22:48:04.276Z | 0 s |
| PM sports WS rows | `pmws.jsonl` | 2026-11-13 22:47:59.897Z | 4 s |
| TheSports MQTT | `ts_mqtt.jsonl` | 2026-11-13 22:48:04.642Z | 0 s |
| PM trades | (none) | not recorded by this capture | `capture.py` has no trade reader — outbox reply 16:29Z §3 |

- All four recorded streams are inside the 10-minute rule (max age 4 min).
- **Goalserve esports + PandaScore still flowing:** goalserve hash log row
  `2026-11-13T22:51:36.313Z` and payload row `recv_ns 1794610296946369046` (22:51:36.9Z);
  pandascore newest complete row 2026-11-13 22:44:35.580Z (append-streamed gzip, read tolerantly);
  both processes running at 22:51Z (`live/goalserve/capture.py` pid 547524, `live/pandascore/ll_capture.py` pid 548127).
- Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.

## P7 — both writers moved off root to the data disk: DONE, recorded 14 Nov 03:15Z (OPEN row P7; IT ruling `IT-REPLY-captures-disk-2026-11-13.md` option (a), clause 22A Type A)

- **Code:** `live/goalserve/capture.py` `OUT`, `PAYDIR` and the 15 GB floor guard now read `/mnt/HC_Volume_107257520/pkarbs/goalserve/`; edit 13 Nov 17:37:34Z, `py_compile` OK, sha256 `279da8f1bea2ad17…`. Revert copy `live/goalserve/capture.py.pre-p7-20261113T173734Z` (paths back to `/vol2/...`).
- **Restart:** tmux session `goalserve` recreated 17:39:07Z (pid 547524, cwd the repo); first hash-log row after the edit `2026-11-13T17:39:07.739+00:00` → ≤94 s from edit to first row. The old process's stop time was not recorded by the session that made the edit.
- **First file on the real VOL2 mount:** `/mnt/HC_Volume_107257520/pkarbs/goalserve/goalserve_20261113.jsonl`, moved intact — 51,232 rows, first row `2026-11-13T02:38:08.116+00:00` (capture start), last `2026-11-14T03:11:15.190+00:00`, still appending. Path proof: `/proc/547524/fd/3` points at that file.
- **`/vol2` can no longer resolve to root:** since 13 Nov 17:44Z `/vol2` is a symlink to the data-disk mount (`ls -ld /vol2` shows `-> /mnt/HC_Volume_107257520`); `findmnt -T /vol2` returns the data disk, not `/`.
- **df /:** before — 17,564,192,768 B free, recorded 13 Nov 15:17Z (pre-move, both status files); after — 17,209,139,200 B free at 14 Nov 03:11Z. Root did not gain the moved bytes because other root writers kept writing across the 11 h between the two readings; the material fact is that neither capture opens a root fd any more, and the data disk holds 72,141,205,504 B free (28% used).
- **Clause-2 route verified live:** writers.conf row `goalserve|/mnt/HC_Volume_107257520/pkarbs/goalserve|pkarbs/goalserve|-|y|hourly`; shipper `ship_raw.sh` every 30 min; ship.log `goalserve shipped=1 deleted=1 kept=0 freed=325186` at 02:30:45Z; `<box>` `pkarbs/goalserve/esports_payloads/` holds the closed hour files `esports_2026111317` … `esports_2026111400` (325 KB – 14.0 MB each), so payload bytes left the disk only after landing on the box.
- **Open, not fixed (a code change, so gated):** the day's hash log is still local-only (the day file stays open until 15 Nov 00:00Z, so the shipper reports `nothing eligible`), and `pandascore BADGZ raw/pandascore_2026111322.jsonl.gz` on every ship run since 01:00Z — that append-streamed gzip has no end marker, the shipper refuses it, so hour 22 neither ships nor deletes (88,771 B local). Fix = a tolerant reader in `ship_raw.sh`.

## #318 recount — Goalserve odds changes (14 Nov 11:16Z; PARTIAL)

Read-only existing script `/vol2/pkarbs/scratch/p318-recount/recount.py`, exit 0. It included 19 hourly files through 09:00Z, explicitly excluding the completed 10:00–11:00Z file; one malformed row skipped. Accordingly the result is partial for the requested interval. Full per-match JSON: `agent/status/p318-recount-2026-11-14.json`; run log: `/vol2/pkarbs/scratch/p318-recount/run-20261114-1114.log`.

Changed participant payloads (consecutive `value_eu`/`suspend` comparison): 78,112 total; CS2 62,908, Dota 2 12,009, other esports 3,195.

| ID | Match | payloads | changed payloads |
|---|---|---:|---:|
| 140832465 | KUUSAMO vs MayBe | 6063 | 7076 |
| 141116256 | Alliance vs Four Magic | 3362 | 4352 |
| 141163317 | Apogee vs Leo Team | 3295 | 3504 |
| 141164392 | MayBe vs mixLVLT | 2519 | 3386 |
| 141164409 | Saint Sinners vs Balkan Outlaws | 297 | 306 |
| 141164753 | ex-RUSTEC vs Nexus | 3244 | 4322 |
| 141164775 | Omega vs Inner Circle Academy | 5100 | 6129 |
| 141165637 | Froglings vs PuckChamp | 1898 | 774 |
| 141165643 | CyberHero vs Xipto | 4045 | 3470 |
| 141165675 | PARIVISION vs Yellow Submarine | 1299 | 640 |
| 141165682 | Team Liquid vs LGD Gaming | 6742 | 2577 |
| 141165693 | Team Spirit vs Froglings | 4348 | 2806 |
| 141192093 | STATE vs EYEBALLERS | 1922 | 2149 |
| 141199605 | Noir Verse vs 6yuBoJlbl | 3102 | 3654 |
| 141199608 | Lavked vs Alliance | 2999 | 3968 |
| 141199612 | ex-INOX vs Saint Sinners | 2612 | 3195 |
| 141202857 | GenOne vs Balkan Outlaws | 2339 | 2998 |
| 141216876 | LGD Gaming vs Legion | 2339 | 1658 |
| 141216926 | Team Spirit vs MOUZ | 1882 | 18022 |
| 141216927 | Inner Circle vs Nemiga | 449 | 84 |
| 141216970 | FURIA vs Falcons | 417 | 3042 |

Polymarket books since 13 Nov 17:06Z: 345 registered matches / 1,858 tokens; 1,022,334 book rows; 90 covered matches; 0 malformed book rows. Captured volume strata: 338 matches <$25k, 7 >=$25k. Book rows by sport/stratum: CS2 <$25k 586,041 (220 covered), CS2 >=$25k 126,691 (5), Dota <$25k 245,567 (118), Dota >=$25k 64,035 (2). PandaScore joined 18 matches; 3 had no registered PM market.
