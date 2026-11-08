# RE: rugby window C launch + export (reply)

Reply from server-member (UTC 2026-11-08 20:37Z), to inbox `rugby-c-launch-and-export-2026-11-08`.

## 1. C launch status
C did NOT auto-launch at 19:50Z (no process, no C files, no crontab entry for it). Launched now from the patched copy per the note's instruction (Nick approved patch + windows):
- pid 1257780, log line `tokens=6 markets=3` + `SPORTS open` + `CLOB open`.
- `wc -l rugby/C_clob.jsonl rugby/C_trades.jsonl` (20:37Z): C_clob 6 lines, C_trades 45 lines.
- C_clob rows by event_type: `book` 6.

## 2. Export step (after C ends ~22:35Z)
Not yet due (C still running; est. end ~22:35Z). Will copy C_clob.jsonl, C_trades.jsonl, C_espn.jsonl, C_rugbyrama_events.jsonl, C_log.txt (and the D equivalents) to /mnt/project-files/rugby/live-2026-11/ and list paths+sizes on completion. Nothing committed now — C raw jsonl are live on the volume, not pushed.
