# cricket capture status (verified 2026-11-12 23:56Z)

- unit thesports-capture-cricket: **inactive (scope deactivated 12 Nov 04:05:18Z)**. Started 10 Nov 04:05Z as a **bounded 48 h trial** (`timeout 172800`, `--no-books`, OUT /vol2/pkarbs/thesports-cricket/2026-11-10); it expired on schedule, not a crash.
- Cricket data this trial: 62,009 ts_mqtt rows (`thesports/cricket/match/v1`), 14.8 MB pmws, ts_poll, log, in the 2026-11-10 OUT dir (ts_mqtt 1.55 GB). Last row ms 1794456317233 = 12 Nov 04:05:17Z.
- slim export (CB6 one-off): **on origin** — `rn1/scores/thesports/final-topics-cricket-slim/` 6506 ts_mqtt gz + pmws/log/ts_poll/counts.json (counts.json shows cricket rows only). Verified on claude/project-thread-vg2ckg.
- capture-b (final-topics-32295b) unchanged and running (pid 2818605, protected, untouched).
- CB12 (MFW auto book manifest): done (mfw main a48aa54/b250d19).
- OPEN (row 5 residual): (1) CB6 2h-timer topic wiring — only meaningful if the cricket capture is restarted (project decision); the data export is already complete. (2) CB7 diary refresh hook into export_timer_2h.sh (auth-param fetch; trial to 16 Nov) — live-producer code change, not applied in this headless nightly slot.

## OPEN / NOT VERIFIED
- Whether the idle cricket capture should be restarted for continued BBL (project decision, not agent's). Restart would be 397a (unchanged code) if the project wants cricket rows to keep flowing.
