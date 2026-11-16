# Dota 2 live capture — 16–17 Nov (update 13:07Z)

- The capture remains active: timeout and Node processes started 06:26:55Z and were present at 13:07Z. All six JSONL outputs advanced during verification; newest valid rows were timestamped 13:07:09–13:07:24Z. Counts / bytes: books 21,296 / 10,969,484; league_games 3,192 / 18,295,338; opendota_live 549 / 119,070; realtime 26,574 / 21,772,038; rt_polls 61,440 / 8,718,571; sportsws 1,341 / 275,532.
- The 13:00Z publisher attempt failed before transfer (rsync exit 255; storage-box authentication denied). Eleven complete compressed chunks remain on the data volume, spanning 09:00Z–13:00Z. The local manifest and offsets remain unchanged at 11:04Z (56 rows); the latest verified remote manifest remains commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`.
- No code, config, crontab or credential change was made; credential values were not read. Raw capture data was not added to Git.
- Final capture coverage/pass-fail is not yet measurable; the run ends 17 Nov 20:30Z. Blocker: valid storage-box authentication is needed before the existing publisher can transfer retained chunks.
