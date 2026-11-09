# outbox: thesports-reexport-markets-now — full spool markets/log now on origin (14:25Z)

RE: `agent/inbox/thesports-reexport-markets-now-2026-11-08.md` — full re-export done, permanent behaviour fixed.

## RESULT
- `final-topics-32295b-slim/markets.jsonl.gz` re-exported WHOLE from live spool: **787 rows**, last ms `1794147289960` (14:14:49Z) — previously 358 rows (last ms 02:01Z). Pushed on origin tip `55206e48` (+190 files @ 14:25:10Z).
- `final-topics-32295b-slim/log.jsonl.gz` re-exported WHOLE: **261 rows**, last ms `1794147597481` — previously 53 rows.
- Root cause of the stale 358-row file: the plumb exporter (`export_slim_32295_plumb.py`) staged the flat copies (markets/pmws/log/ts_poll) under `zz-src-<name>` while the timer's commit loop looks for `<name>.gz`, so the `-f` existence test never matched and those files were never refreshed on origin. Changed the staging name to `<n>.gz`; re-ran the approved exporter; the full files now commit every 2-hour timer run.
- Permanent: the 2-hourly timer (`export_timer_2h.sh`, cron `0 */2 * * *`) now copies the WHOLE markets.jsonl and log.jsonl each run (same guard, slim dir only). Next timer fire 16:00Z.
- No capture change; spool untouched; nothing approved was skipped.

## DATA
- Live spool: `/vol` thesports final-topics-32295b `markets.jsonl` 787 rows / `log.jsonl` 261 rows (capture-b scope active, ts_mqtt growing 14:26Z).
- Committed: `rn1/scores/thesports/final-topics-32295b-slim/markets.jsonl.gz` (787), `log.jsonl.gz` (261) on `claude/project-thread-vg2ckg` @ 55206e48.

Count: notes run 1, outstanding 0, PENDING open 0.
