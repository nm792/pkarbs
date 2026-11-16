# Dota 2 live capture — 16–17 Nov

- Capture is live: timeout PID 1700947 and Node PID 1700948, started 06:26:55Z, 400 MiB cap, zero swap. Output continued growing at 11:04Z.
- The 09:00/09:30/10:00/10:30/11:00Z scheduled copies failed with storage-box SSH authentication errors. The existing publisher was run manually at 11:04Z: seven complete gzip deltas transferred and passed checksum verification; manifest commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e` is on this branch.
- No capture or publisher code/config/crontab changes. Final capture coverage remains unmeasured until the run ends at 17 Nov 20:30Z. Scheduled future copies remain unverified.
- Current status and row counts: `agent/status/dota-live-capture-2026-11-16.md`.
