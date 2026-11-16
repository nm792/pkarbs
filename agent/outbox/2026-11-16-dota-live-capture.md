# Dota live capture — update at 2026-11-16 10:45Z

- Capture remains active (timeout PID 1700947, Node PID 1700948), started 06:26:55Z with 400 MiB cap and zero swap. Output advanced through 10:44Z; observed totals: realtime 11,980 rows, rt_polls 28,171, books 7,539.
- Scheduled publisher attempts at 09:00Z, 09:30Z, 10:00Z, and 10:30Z failed with storage-box authentication errors. The existing approved publisher ran manually at 10:45Z and caught up seven complete gzip deltas; all seven transfers passed checksum dry-runs. New chunk rows: books 2,240; league_games 261; opendota_live 44; realtime 2,098; rt_polls 4,682; sportsws 142; capture log 6.
- Manifest `manifest/dotacap-2026-11-16.tsv` was pushed at `7da31552586b1c4e1e955dc271386f6c407cdc86`. Raw data remains on `<box>`, not Git. Code, config and crontab are unchanged.
- Final coverage/pass-fail remains unmeasured; the capture continues through 17 Nov 20:30Z.
