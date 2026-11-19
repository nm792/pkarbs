# Weekend perp logger live sample — 2026-11-16

Source revision: pkarbs `origin/claude/project-thread-vg2ckg` at `2d75cca9515ccf9f653fc59678c05892e5cd755f`.

- Hyperliquid: `weekend-perps-logger.service`, active, `Restart=always`; PID 2907769; process start 2026-11-14 06:08:53Z. Sample window 09:33:00–10:03:30Z: 5,640 rows, first 09:34:26Z, last 09:59:58Z, 0 error rows, 0 malformed lines. Output on the data volume, 10,193,654 bytes at 10:03:02Z.
- Polymarket: `weekend-perps-pm-logger.service`, active, `Restart=always`; PID 1973687; process start 2026-11-16 09:16:10Z. Sample window 09:33:00–10:03:30Z: 217 rows across all 7 requested symbols, first 09:33:10Z, last 10:03:10Z, 0 error rows, 0 malformed lines. Output on the data volume, 52,246 bytes at 10:03:12Z.

Both services were already active; neither was restarted. The loggers use public read-only data and no credentials or orders. Thirty-minute live sample verified. The task’s 20 Nov 06:00Z persistence check remains due.
