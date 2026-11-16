# Weekend perp logger task — completion

Status: DONE. The original 12 Nov smoke/service request was superseded by `agent/TASK-weekend-perps-loggers-install-2026-11-16.md`; its live-sample report supplies the stronger verification.

- The 30-minute sample on 16 Nov recorded 5,640 Hyperliquid rows and 217 Polymarket rows; both had zero malformed/error rows. The detailed sample, timestamps and measured file sizes are in `agent/outbox/weekend-perps-logger-sample-2026-11-16.md`.
- Read-only live check at 21:59Z: both services active with `Restart=always`. The Hyperliquid file's latest write was 21:54:09Z; the Polymarket file's latest write was 21:58:11Z. Both files are under `/vol2/weekend-perps/`.
- Historical candle availability and the fixed backfill choices are recorded in `weekend-perps/LOCKED-RULE.md`; backfill artifacts are in `weekend-perps/backfill-2026-11-16/`.
- The historical five-minute smoke is not separately evidenced in the current report. The later 30-minute live sample and current write checks cover reachability and continued operation; no code change, key, account, signing, or order was involved. Raw logger files remain on the data volume and were not committed.

This reply closes the legacy task; the replacement install task's 20 Nov 06:00Z persistence check remains separately due.
