# Dota live capture — update at 2026-11-16 10:23Z

## Result
- Capture is active as `dotacap-2026-11-16.service` (Node PID 1700948; unit MainPID 1700947), started 06:26:55Z, with a 400 MiB memory cap and zero swap. Output files advanced through 10:22Z.
- The scheduled publisher encountered storage-box authentication failures at 09:00Z, 09:30Z, and 10:00Z. I ran the existing approved publisher at 10:22Z; it caught up seven gzip deltas, verified each transfer with checksum dry-runs, and pushed the updated manifest. Counts: books 5,210; league_games 1,008; opendota_live 175; realtime 7,614; rt_polls 18,604; sportsws 332; capture log 47 rows.
- Manifest: `manifest/dotacap-2026-11-16.tsv`, 42 entries; push commit `4d76d5dbc8bf496c7c34d1c07f88cbec6e42a641`. Raw data remains on `<box>`, not Git.
- Final coverage/pass-fail remains unmeasured; capture is scheduled through 17 Nov 20:30Z.

## Publisher and revert
- Existing publisher implementation and approved cron lines are unchanged. The manual run succeeded despite the earlier scheduled authentication errors.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected. The final line removes both publisher entries after the last copy.
