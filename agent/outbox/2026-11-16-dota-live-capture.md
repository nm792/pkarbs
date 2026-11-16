# Dota 2 live capture — 16–17 Nov (update 12:47Z)

- Capture was active at 12:47Z: timeout and Node processes were both present; output files advanced through 12:47:27Z. Current rows: books 18,627; league_games 2,959; opendota_live 509; realtime 24,264; rt_polls 56,668; sportsws 1,163.
- Publisher remains blocked before transfer by storage-box authentication. The latest publisher attempt at 12:30Z failed with rsync exit 255 (public-key/password authentication denied); the 12:30 attempt also recorded exit 12. The local publisher manifest remains at 11:04Z (56 rows), with 10 compressed chunks retained locally; publisher offsets remain at the 11:04Z values and did not advance on these failures. The latest verified remote manifest remains commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`.
- No code, configuration, crontab or credential change was made. Credential values were not read. Final capture coverage/pass-fail remains unmeasured.
- Blocker/unblock: valid storage-box authentication is required before the existing publisher can transfer the retained chunks.
