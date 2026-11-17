# Dota 2 live capture — update 01:15Z, 17 Nov

- Capture remains active (timeout PID 1700947; Node PID 1700948), started 06:26:55Z on 16 Nov with 400 MiB cap and zero swap; configured through 20:30Z today.
- At 01:15Z live counts: books 107,624 (last write 22:59Z), league_games 11,585 (01:15Z), opendota_live 1,987 (01:14Z), realtime 105,890 (01:15Z), rt_polls 237,356 (01:15Z), sportsws 7,123 (23:29Z). The capture log last changed at 00:53Z and contains 453 league-query errors. Final series coverage and the task pass/fail threshold are not yet established.
- The 01:00Z scheduled publisher hit storage-box authentication errors. The existing publisher was run at 01:13Z; seven complete gzip deltas transferred and passed checksum verification. The manifest now has 70 chunks / 526,742 rows and is pushed at `46bd0f3c32383eb54e042a9c3a6d08f046b8ba81`.
- No capture/publisher code, configuration, crontab or service changes; no credential values read or changed. Later scheduled transfers and final coverage remain unverified until the capture ends at 20:30Z.
- Current details: `agent/status/dota-live-capture-2026-11-16.md`; manifest: `manifest/dotacap-2026-11-16.tsv`.
