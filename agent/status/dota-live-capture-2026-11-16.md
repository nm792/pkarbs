# Dota live capture — current status (2026-11-16 12:47Z)

- Capture: timeout and Node processes were active at 12:47Z; output advanced through 12:47:27Z. Rows: books 18,627; league_games 2,959; opendota_live 509; realtime 24,264; rt_polls 56,668; sportsws 1,163.
- Publisher: the recurring 30-minute publisher remains installed. Latest attempts failed before transfer (rsync exit 255 authentication denied; a prior attempt exited 12). Local publisher manifest remains at 11:04Z with 56 rows; 10 complete compressed chunks are retained locally. Publisher offsets remain unchanged at the 11:04Z state. Latest verified remote manifest: `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`.
- No code, config, crontab or credential change was made; credential values were not read. Final coverage/pass-fail is not measured.
- Waiting for valid storage-box authentication; no further transfer retry made in this run.
