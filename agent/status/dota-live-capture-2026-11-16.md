# Dota live capture — current status (2026-11-16 12:03Z)

- Running: timeout PID 1700947 and Node PID 1700948; both observed active at 12:02:51Z. Configured capture window ends 2026-11-17 20:30Z. Output continued growing at the last check: books 13,485 rows; capture.log 2,694; league_games 2,442; opendota_live 421; realtime 19,674; rt_polls 46,056; sportsws 785.
- Publisher: recurring 30-minute line remains installed. Transfers fail before the first file with rsync exit 255 (storage-box authentication rejected). Latest successful remote manifest is `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`, through 11:04Z. Nine complete chunks are retained locally; publisher state remains at 11:04Z, so failed transfers did not advance offsets.
- No code, config, crontab or credential change was made. No credential values were read. Final coverage/pass-fail is not measured before the capture ends.
- Revert: not applicable; no change made.
