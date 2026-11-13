# thesports diary + slim — 2026-11-07 (ack to `thesports-diary-priority-2026-11-07`)

round 2026-11-07T05:1xZ

- `match/diary` run for today and yesterday (UTC) per sport, redacted raw saved to
  `rn1/scores/thesports/diary/<sport>-<date>.json` (committed on this branch):
  - basketball: 405 matches (11-07), 221 (11-06) — team names present via results_extra
  - tennis:     108 (11-07), 115 (11-06)
  - lol:        1 match — **Worlds 2026 knockout: T1 vs Karmine Corp** (match_time 1794002700)
  - dota2:      22 (11-07), 22 (11-06)
  - csgo:       29 (11-07), 29 (11-06)
  - esports + cs2 paths: `{"err":"URL is not authorized to access, please contact our business staff."}` (recorded in the json, not a crash)
- Fresh slim export of live chunk `final-topics-32295` (started 2026-11-07T04:00Z) committed:
  ts_mqtt 6.2MB gz (basketball + tennis topics delivering this window), books_mid, markets, pmws, log; `counts.json` per topic|hour captured.
- LoL: MQTT 0 msgs + HTTP `/v1/lol/match/detail_live` → "URL is not authorized". Resubmit to TheSports to authorize LoL (task priority #1, Worlds semis 7-8 Nov). Not my approval to grant.
- Credentials never printed, committed, or included in any file. Diary JSON redacted (`<user>`/`<secret>`).
- No separate go needed beyond the existing GO (Nick 6 Nov 09:23Z, task header) — this is the read-only team-name lookup step it names.
