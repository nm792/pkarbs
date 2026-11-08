# agent/outbox/thesports-export-now-2026-11-08 — reply to inbox note (04:58Z)

**TheSports slim export requested in the note is DONE — committed at 06:04Z**, capture is live.

**Capture status:** running (capture-b). `capture.py .../final-topics-32295b` process alive (start_writer-launched), writing fresh rows continuously; last raw writes 06:16Z (ts_mqtt, books).

**Committed slim (share, regenerated 06:08Z; commits 727b648a @06:03:16Z + 2e64be46 @06:04:04Z):**
- `ts_mqtt` 216,580 rows
- `books`   493,769 rows
- `markets` 424 rows
- `pmws`    3,103 rows
- `log`     121 rows
- `ts_poll` 70 rows

Live raw (06:16Z): ts_mqtt 220,449 · books 504,509 · markets 432 · pmws 3,121.

**Diary:** refreshed per prior notes; cs2/esports diary endpoint still "URL is not authorized". 

**Next export:** every 2 h via cron `0 */2 * * * export_timer_2h.sh` → next at 08:00Z.
