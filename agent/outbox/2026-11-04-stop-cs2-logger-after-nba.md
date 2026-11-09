# outbox/2026-11-04-stop-cs2-logger-after-nba — acknowledged; stop scheduled AFTER NBA capture

Understood: cs2-ws-logger must keep running through 06:45Z 5 Nov (NBA window), then stop + move to storage box. No stop action now.

- Logger confirmed RUNNING (node pid 2758025 under watchdog pid 1533833; systemd transient unit cs2-logger.service shows the earlier 12 h timeout end, watchdog keeps the process alive).
- Will keep it up (restart once as-now if its 12 h timeout lapses before 06:45Z 5 Nov) per the note.
- After 06:45Z 5 Nov: final hourly-style copy to rn1/scores/cs2/server-2026-11/, stop watchdog then logger, confirm both gone, move /root/cs2logger/out to storage box `pkarbs/cs2logger/out/` per the storage-offload ruling, report in agent/status/cs2-ws-logger.md (STOPPED, rows, GB, df before/after).
- This is a scheduled future action; no approval needed (noted as Nick's go-ahead).
