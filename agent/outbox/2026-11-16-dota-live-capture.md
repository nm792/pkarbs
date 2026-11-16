# Dota 2 live capture — 16–17 Nov (update 11:24Z)

- Capture remains active: timeout PID 1700947 and Node PID 1700948, started 06:26:55Z, 400 MiB cap, zero swap. At 11:23Z row counts: books 10,024; capture.log 751; league_games 2,000; opendota_live 344; realtime 15,379; rt_polls 36,791; sportsws 660.
- Existing publisher retry at 11:24Z failed before transfer with storage-box SSH `Permission denied (publickey,password)` (rsync exit 255). No new manifest commit; latest verified remote copy is through 11:04Z, commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`. A local books chunk from the failed attempt remains unshipped; its state offset was not advanced.
- The 30-minute publisher cron remains installed; no code/config/crontab or credential changes. Final coverage remains unmeasured until the capture ends 17 Nov 20:30Z.
- Current details: `agent/status/dota-live-capture-2026-11-16.md`.
