# TASK (PRIORITY 1, run BEFORE the Netflix and Spotify recorders): TheSports export + cricket + diary

From: Claude in the PK arbs TheSports thread (10 Nov 2026, 10:50Z). Requested by Nick via the coordinator. Status: OPEN. This outranks TASK-netflix-recorder and TASK-chart-recorder: the free TheSports trial ends 16 Nov and every missed 2 h export costs unrecoverable test count (tennis 29/60 matches, Dota 13/40 games; locked tests).

## Question (one only)
Do the TheSports 2 h slim export, the cricket export and the 10 Nov diary all land on origin?

## Pass / fail, fixed before running
- PASS: (1) a `thesports 2h slim export 32295b` commit newer than 06:16Z 10 Nov, whose markets.jsonl.gz last `ms` is within 30 min of the export time; (2) CHANGE-BATCH #6 applied (Nick approved 05:12Z): cricket ts_mqtt/pmws/log rows from thesports-cricket/2026-11-10 in a slim dir `final-topics-cricket-slim`; (3) diary json for 2026-11-10 (tennis, dota2, csgo, lol, basketball) refreshed now.
- FAIL: report which of the three failed and the last 20 lines of its output. No retries beyond one.

## Run
Same scripts as before (export timer, then the diary method used at 09 Nov 08:03Z, creds redacted, nothing secret in git). Read-only for TheSports and Polymarket, no orders, delete nothing, deletion guard on every commit path.

## After
Make the diary a daily step before the first export of each UTC day (CHANGE-BATCH #7) and say why the 08:15Z and 10:15Z timer runs did not land. Reply in `agent/outbox/thesports-export-priority-2026-11-10.md` with commit shas and last `ms` per file.
