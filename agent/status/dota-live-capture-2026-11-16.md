# Dota live capture — update 2026-11-16 11:24Z

## Result
- Capture is active: timeout PID 1700947 and Node PID 1700948, started 06:26:55Z, with 400 MiB memory cap and zero swap. At 11:23Z counts were books 10,024; capture.log 751; league_games 2,000; opendota_live 344; realtime 15,379; rt_polls 36,791; sportsws 660. Output mtimes advanced through 11:23Z.
- Existing publisher retry at 11:24Z failed before transferring its first chunk: storage-box SSH authentication returned `Permission denied (publickey,password)`, rsync exit 255. No new manifest was pushed. The latest verified remote manifest remains commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e` (data through the successful 11:04Z run).
- The failed attempt left a local unshipped `books.20261116T112413Z.jsonl.gz` in the publisher chunks directory; publisher state offset was not advanced for that chunk. This is local evidence, not a verified box copy. No code, configuration or crontab was changed.
- Final coverage/pass-fail remains unmeasured; capture is scheduled through 17 Nov 20:30Z.

## Publisher and revert
- Recurring 30-minute publisher cron remains installed. Scheduled and manual attempts after the 11:04Z successful run are not verified because SSH authentication is failing. No credentials were read or changed.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected.

## Prior update (11:05Z; historical)
- Capture remains active (timeout PID 1700947; Node PID 1700948), started 06:26:55Z with 400 MiB memory cap and zero swap. At 11:04Z the output files were still growing; latest observed totals: 9,095 books, 1,776 league_games, 306 opendota_live, 13,859 realtime, 32,351 rt_polls, 593 sportsws, and 161 capture-log rows.
- The scheduled publisher failed at 09:00, 09:30, 10:00, 10:30, and 11:00Z with storage-box SSH authentication failures. I ran the existing approved publisher manually at 11:04Z. It transferred and checksum-verified seven complete gzip deltas, then pushed the manifest; new chunks contain 1,561 books, 226 league_games, 38 opendota_live, 1,889 realtime, 4,212 rt_polls, 107 sportsws, and 100 capture-log rows.
- Manifest: `manifest/dotacap-2026-11-16.tsv`; verified commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`. Raw data remains on `<box>`, not Git. No capture/publisher code or crontab changes were made.
- Final coverage/pass-fail remains unmeasured; capture is scheduled through 17 Nov 20:30Z.

## Publisher and revert
- Existing publisher and cron lines remain unchanged. Scheduled publishing has an unresolved SSH-auth failure; the 11:04Z manual run caught up the deltas through that time. Do not treat future scheduled copies as verified.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected.

Historical 11:05Z update; superseded by the current 11:24Z status above.
