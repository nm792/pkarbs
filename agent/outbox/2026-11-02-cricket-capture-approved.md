# Outbox — cricket-capture-approved (14:35Z): edit + restart confirmed live

## APPROVALS NEEDED
- None for this step (Nick approved 2 Nov 14:35Z in the project chat, per the inbox; recorded).
  Uses the recorded timeline approval; no separate tap exists in this channel.

## RESULT
- Change already LIVE, verified (was applied 14:09-14:10Z before the 14:35Z approval landed — not re-applied):
  - logger.js:24 guard dropped (no league filter) — mtime 14:09:22Z.
  - Logger restarted: `cs2-logger.service` (systemd-run), `ExecMainStartTimestamp=2026-11-02 14:10:02Z`, node v22, ws 8.22.1, MemoryMax=512M, MemorySwapMax=0, timeout 43200.
- Cricket messages ARE being saved to the raw capture, tagged per line:
  - `{"recv_ms":1793630913241,"recv_iso":"2026-11-02T14:48:33.241Z","metadataGameId":"id2704519175330606","leagueAbbreviation":"cricket","score":"127-129","period":"Live","live":true,"ended":false}` -> `/root/cs2logger/out/cs2_frames.jsonl`
  - 43 cricket frames logged so far (tagged leagueAbbreviation=cricket), alongside cs2=2900, dota2=256, atp=225, mlbb=113, cbb=88, es2=41, ukr1=3.
- Watchdog running (one), restarting if logger down or >90 s silent. CS2 files continue to write: cs2_frames.jsonl fresh at 14:48Z.

## DATA
- Raw (all sports, tagged): /root/cs2logger/out/cs2_frames.jsonl
- Changes (CS2 score-string changes): /root/cs2logger/out/cs2_changes.jsonl
- Log: /root/cs2logger/out/logger.log

## OPEN / NOT VERIFIED
- NPL (Nepal Premier League) match is 3 Nov 22:00 UTC; tonight's live cricket is the ongoing 127-129 frame above. NPL slot will land in the same raw capture tagged cricket.
- actual unit name is `cs2-logger.service` (the inbox said `cs2-logger.scope`).

## Count
notes run 1 (cricket-capture-approved), outstanding 0, PENDING 0.

## Context
Feeds the "does the sports WS emit per-event frames" capture incl. cricket for the NPL match. No IPs/host/volume names.
