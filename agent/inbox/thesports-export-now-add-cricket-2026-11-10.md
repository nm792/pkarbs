# Export now, and add cricket to the 2 h timer (CHANGE-BATCH #6 is APPROVED by Nick, 10 Nov 05:12Z)

1. Run a one-off 2 h slim export now (the 08:15Z one did not land; last is 06:16Z).
2. Apply CHANGE-BATCH #6: include the cricket ts_mqtt/pmws/log rows (thesports-cricket/2026-11-10) in the timer export, own dir `final-topics-cricket-slim`. Do a one-off cricket export too.
3. Do the 10 Nov diary refresh again now, and make the daily diary hook (#7) run before the first export of each UTC day. Today's matches after 04:52Z are unnamed otherwise.
4. Reply in `agent/outbox/thesports-export-now-add-cricket-2026-11-10.md` with commit shas and the last `ms` per file, plus why 08:15Z did not run if you can tell.
