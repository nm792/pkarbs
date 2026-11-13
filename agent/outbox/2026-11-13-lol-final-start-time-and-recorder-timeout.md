# Reply: LoL Worlds final start time + recorder timeout confirmation (P9) — measured 13 Nov 22:46-22:51Z

Answers `agent/inbox/2026-11-13-lol-final-start-time-and-recorder-timeout.md` (and closes the
proof IT asked for in `IT-REPLY-recorder-timeout-2026-11-13.md`, which merged #311/#312 item 2
into OPEN row P9, deadline 14 Nov 06:00Z — this is filed 7 h early).

## Item 1 — final start time (posted in `agent/status/goalserve.md`, section "LoL final start")

- **MEASURED: 2026-11-14 19:00:00Z**, Gen.G Esports vs BILIBILI GAMING, `blockName "Finals"`,
  `state "unstarted"`, match id `115660540726095133`.
- Source: official schedule call `esports-api.lolesports.com/persisted/gw/getSchedule`
  (`hl=en-US`, `leagueId=98767975604431411` = Worlds, id from `rn1/scores/lol/winmodel/list_games.py`),
  **HTTP 200, response fetched 2026-11-13T22:46:24Z**; 80 events read, this is the only Worlds event
  with `startTime >= 2026-11-12`. Corroborated by `getEventDetails` on the same match id
  (HTTP 200 at 22:46:55Z, same two teams; its event-level `startTime` is null, so the time comes
  from `getSchedule` only). Read from the response, not from memory or web search; no key material
  in this file.

## Item 2 — recorder stop confirmation (also in `agent/status/goalserve.md`)

- **New launch text, no `timeout 552000`:** `ExecStart="/usr/bin/python3" "-I" ".../live/thesports/capture.py" "<data-vol>/final-topics-32295b" "160" "--share" "<data-vol>/final-topics-32295b/share"`,
  `EnvironmentFile=/etc/pkarbs/thesports.env`, no timeout line in the unit; the guard's relaunch
  line has none either. capture.py bounds itself at 160 h (runs past the final).
- **Guard:** `*/5 * * * * bash /root/pkarbs/live/thesports/guard_capture_b.sh >> /var/log/thesports_capture_guard.log`
  (flock-guarded). Absence OR newest row >600 s across books/pmws/ts_mqtt/log → TERM + relaunch,
  restarts logged (ts_poll excluded: written only on body change). Ticks `rc=0` through 22:45:01Z;
  live process pid 898340 started by the guard at 18:16:51Z; relaunch proven live 18:16:51Z
  (`creds:true`, `ae85a3d4c9`), STALE branch dry-run tested (`GUARD_MAX_AGE=-1`, `3fc673c556`).
- **Revert copy:** `crontab.pre-p9-guard-20261113T1818Z.txt` (pre-guard crontab) +
  `rm /root/pkarbs/live/thesports/guard_capture_b.sh`.
- **Newest row UTC per stream** (measured 22:48:04Z, newest row of each file):

| stream | newest row UTC | age |
|---|---|---|
| PM registration (`markets.jsonl`) | 2026-11-13 22:44:09.169Z | 4 min |
| CLOB books (`books.jsonl`) | 2026-11-13 22:48:04.276Z | 0 s |
| PM sports WS (`pmws.jsonl`) | 2026-11-13 22:47:59.897Z | 4 s |
| TheSports MQTT (`ts_mqtt.jsonl`) | 2026-11-13 22:48:04.642Z | 0 s |
| PM trades | not recorded — `capture.py` has no trade reader (outbox 16:29Z §3) | n/a |

- **Goalserve esports payload rows and PandaScore rows still flowing:** goalserve hash log row
  2026-11-13T22:51:36.313Z, payload row 22:51:36.9Z, pandascore newest complete row 22:44:35.580Z;
  both processes up at 22:51Z. All four recorded streams are inside the 10-minute rule.
- Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.

OPEN / NOT VERIFIED: none — both items of the note are measured and posted.
