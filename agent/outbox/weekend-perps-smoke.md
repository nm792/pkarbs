# Weekend perp logger smoke — 2026-11-16

Status: DONE; the original 12 Nov logger task is superseded operationally by `agent/TASK-weekend-perps-loggers-install-2026-11-16.md` and its 30-minute live-sample report.

- Hyperliquid logger: `weekend-perps-logger.service` was active with `Restart=always`; the report records a 30-minute sample from 09:33:00–10:03:30Z: 5,640 rows, first 09:34:26Z, last 09:59:58Z, zero error rows and zero malformed lines.
- Polymarket logger: `weekend-perps-pm-logger.service` was active with `Restart=always`; the same sample window had 217 rows across all 7 requested symbols, zero error rows and zero malformed lines.
- At 19:41Z both services were still active. Their data files were on the data volume and had fresh writes: Hyperliquid file mtime 19:39:43Z; Polymarket file mtime 19:41:13Z. No restart or code change was made.
- Historical candles are available for the locked backfill: `weekend-perps/LOCKED-RULE.md` records xyz hourly candles back to 22 Apr 2026 and 1-minute candles for the recent window; the corresponding backfill artifacts are under `weekend-perps/backfill-2026-11-16/`.

Evidence: `agent/outbox/weekend-perps-logger-sample-2026-11-16.md`, `weekend-perps/LOCKED-RULE.md`, and current service/file checks on Prime. The separate 20 Nov 06:00Z persistence check remains due under the replacement install task.
