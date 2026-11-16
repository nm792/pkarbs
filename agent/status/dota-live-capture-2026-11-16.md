# Dota live capture — update at 2026-11-16 10:45Z

## Result
- Capture remains active (timeout PID 1700947, Node PID 1700948), started 06:26:55Z with 400 MiB memory cap and zero swap. Live output advanced through 10:44Z; current files contain 11,980 realtime rows, 28,171 book-poll rows, and 7,539 book rows.
- Scheduled publisher attempts at 09:00Z, 09:30Z, 10:00Z, and 10:30Z failed with storage-box authentication errors. At 10:45Z I ran the existing approved publisher manually; it transferred and checksum-verified seven complete gzip deltas, then pushed the manifest. The new chunks contain 2,240 books, 261 league_games, 44 opendota_live, 2,098 realtime, 4,682 rt_polls, 142 sportsws, and 6 capture-log rows.
- Manifest: `manifest/dotacap-2026-11-16.tsv`; push commit `7da31552586b1c4e1e955dc271386f6c407cdc86`. Raw data remains on `<box>`, not Git. No capture or publisher code/config/crontab changes were made.
- Final coverage/pass-fail remains unmeasured; capture is scheduled through 17 Nov 20:30Z.

## Publisher and revert
- Existing approved publisher and cron lines are unchanged. The failed scheduled copies were caught up by the successful manual run; the next scheduled run has not yet been verified.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected.
