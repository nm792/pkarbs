# Dota 2 live capture — update 13:54Z, 16 Nov

- Capture active at 13:53:49Z; all six output files grew through 13:53:50Z. Valid rows / bytes: books 30,553 / 15,720,312; league_games 3,726 / 25,242,311; opendota_live 641 / 159,458; realtime 31,689 / 25,970,838; rt_polls 72,523 / 10,301,881; sportsws 1,811 / 374,083. Malformed rows: zero. Latest receive timestamps: 13:53:32–13:53:50Z.
- The 13:30Z publisher attempt failed before transfer (authentication denied; rsync exit 255). The publisher log also records exit 12 at 12:30Z and repeated exit 255. The 13:00Z and 13:30Z chunks are not verified as shipped; no remote copy was verified in this run.
- No capture data was added to Git. No code/config/crontab/credential changes were made, and no credential value was read. Final coverage/pass-fail is not yet measurable; capture remains scheduled through 17 Nov 20:30Z and storage-box authentication blocks verified transfer.
