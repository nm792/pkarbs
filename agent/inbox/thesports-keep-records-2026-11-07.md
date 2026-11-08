# Request to Hermes: keep all TheSports and Polymarket records (written 2026-11-07T07:40Z)

Nick, 07:38Z: "we need to assess this trial properly so keep the records".

What to do (read-only, no orders, no money, no new services):
1. Do not delete or overwrite any TheSports or Polymarket book capture, raw or slim, for the whole trial. Includes `final-topics-*`, `books`, `ts_mqtt`, `ts_poll`, `pmws`, `markets`, `log`, diary files.
2. Keep exporting and committing the slim export (`live/thesports/export_slim.py`), now and every 2 h as already running, raw data to /vol2 plus the storage box per the server charter (nothing raw on the root disk; 15 GB free rule unchanged).
3. If a disk or retention rule forces a deletion, stop and say so in `agent/outbox/thesports-keep-records-ack-2026-11-07.md` instead of deleting. Write that ack this round (even "started").
