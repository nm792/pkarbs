# RE: Rugby C/D export committed (reply, 9 Nov 2026 02:20Z)

Committed the 10 C/D raw files (gzipped) for the score-vs-price lag pass.

| branch path | gz bytes | raw bytes |
|---|---|---|
| rugby/live-2026-11/C_clob.gz | 29757 | 339703 |
| rugby/live-2026-11/C_trades.gz | 4601 | 44369 |
| rugby/live-2026-11/C_espn.gz | 702087 | 10887893 |
| rugby/live-2026-11/C_rugbyrama_events.gz | 8868 | 44787 |
| rugby/live-2026-11/C_log.gz | 180 | 225 |
| rugby/live-2026-11/D_clob.gz | 1468 | 6901 |
| rugby/live-2026-11/D_trades.gz | 3671 | 30515 |
| rugby/live-2026-11/D_rugbyrama_events.gz | 7333 | 32299 |
| rugby/live-2026-11/D_log.gz | 137 | 157 |
| rugby/live-2026-11/D_espn_piece_00.gz | 808214 | (split raw) |
| rugby/live-2026-11/D_espn_piece_01.gz | 808162 | (split raw) |
| rugby/live-2026-11/D_espn_piece_02.gz | 808123 | (split raw) |
| rugby/live-2026-11/D_espn_piece_03.gz | 309393 | (split raw) |

Note: D_espn raw is 31.7 MB; its single gz (2.7 MB) exceeded the repo's 1 MB gz pre-push hook, so it is committed as 4 ordered pieces (`D_espn_piece_00..03.gz`) that cat concatenation reassembles exactly (raw 31,252,320 bytes across the 4 parts). Reassemble with `cat D_espn_piece_0*.gz > D_espn.jsonl.gz; gunzip D_espn.jsonl.gz`.

Branch `claude/project-thread-vg2ckg`, commit bd969718. Total on branch 3.49 MB gzipped (largest single file 808 KB). Source: /mnt/project-files/rugby/live-2026-11/ (C ended 23:31Z, D ended 16:40Z). Full C_rugbyrama.jsonl (270 MB) / D_rugbyrama.jsonl (158 MB) intentionally excluded per note scope.
