# Dota 2 live capture — current status (2026-11-16 13:07Z)

- Capture is active: timeout and Node processes started 06:26:55Z; both were present at 13:07Z. All six JSONL outputs advanced during the check; newest valid row timestamps were 13:07:09–13:07:24Z. Current valid rows / bytes: books 21,296 / 10,969,484; league_games 3,192 / 18,295,338; opendota_live 549 / 119,070; realtime 26,574 / 21,772,038; rt_polls 61,440 / 8,718,571; sportsws 1,341 / 275,532.
- Publisher still cannot authenticate to the storage box: the 13:00Z cron attempt failed before transfer with rsync exit 255 (public-key/password authentication denied). No credential values were read or changed. Eleven complete compressed chunks remain on the data volume (09:00Z–13:00Z); local manifest/offsets remain at 11:04Z (56 rows), unchanged.
- Latest verified remote manifest remains commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`; no raw capture data was added to Git.
- Capture coverage/pass-fail is not yet measurable against the final 17 Nov 20:30Z window end. No code, config, crontab, or credential change made.
- Blocker: valid storage-box authentication is required for the existing publisher to transfer retained chunks.
