# Re-export of the cumulative TheSports files — DONE (reply to thesports-markets-overwritten-2026-11-11)

Cause: the 04:07Z export run staged the four cumulative files from a truncated spool window and shipped the short slice (markets 358 rows -> 7 Nov) on top of the full ones. The underlying spool now holds the complete data.

Fix applied on `claude/project-thread-vg2ckg`:
- **Re-export commit `0e384c85`** — the four cumulative files rebuilt whole from the full spool (all rows since 6 Nov, gzipped, replacing the reviewer-restored slice).
- **Guard commit `15407a49`** — `live/thesports/export_timer_2h.sh` now refuses to stage any of the four cumulative `.jsonl.gz` (markets/pmws/log/ts_poll) that shrank >5% vs the committed blob on TIP; a truncated source can never overwrite the good file again.

Final committed values (commit `0e384c85`):
| file | rows | last ms (UTC) |
|---|---|---|
| markets.jsonl.gz | 2320 | 2026-11-11T05:12:02Z (1794373922144) |
| pmws.jsonl.gz | 93586 | 2026-11-11T05:37:32Z (1794375452004) |
| log.jsonl.gz | 1240 | 2026-11-11T05:12:39Z (1794375159185) |
| ts_poll.jsonl.gz | 2603 | 2026-11-09T01:37:59Z (1794188279880) |

UTC: 2026-11-11 ~05:35Z.
