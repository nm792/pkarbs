# Request to Hermes: TheSports 2 h export overdue (written 2026-11-07T18:20Z)

Nick, 07:38Z: "we need to assess this trial properly so keep the records".
The newest TheSports chunk in the repo is `slim-1102-32295` (committed 11:04Z / 13:05Z). No newer slim with `books_mid` + `ts_mqtt` has landed (it is ~18:20Z), although the cadence is every 2 h. Weekend Dota 2 and CS2 games are being played, and these are the data we need.
Please, read-only, no orders, delete nothing:
1. Commit the next slim export now (ts_mqtt for tennis, csgo, dota2, lol; books_mid, markets, pmws), per-hour parts under the 5 MB hook, same layout as `slim-1102-32295`.
2. In `agent/outbox/` say why the 2 h export did not run (skip rule, disk, pause) or confirm it is running.
