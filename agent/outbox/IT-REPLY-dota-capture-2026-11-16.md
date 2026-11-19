# Reply: IT Dota capture routing (#357)

- The requested single read-only capture remains active: timeout PID 1700947 and Node PID 1700948, started 06:26:55Z with 400 MiB cap and zero swap.
- The 30-minute no-model publisher cron was already present. Scheduled runs through 11:00Z failed with storage-box SSH authentication errors; the existing publisher was run manually at 11:04Z and transferred/checksummed seven complete deltas. Manifest commit: `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`.
- Current status and row counts are in `agent/status/dota-live-capture-2026-11-16.md`; task report is `agent/outbox/2026-11-16-dota-live-capture.md`. Coverage remains open until the capture ends 17 Nov 20:30Z.
