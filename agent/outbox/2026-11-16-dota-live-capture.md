# Dota 2 live capture — update 14:12Z, 16 Nov

- Capture active at 14:11Z; six output streams had fresh writes through 14:11:57Z. Valid rows / bytes: books 34,058 / 17,530,926; league_games 3,925 / 27,879,850; opendota_live 677 / 177,134; realtime 34,024 / 28,059,164; rt_polls 77,367 / 10,993,698; sportsws 2,000 / 414,543. Malformed rows: zero in each file.
- The 14:00Z publisher attempt failed before transfer (rsync exit 12; SSH authentication denied). Earlier 12:30Z, 13:00Z and 13:30Z attempts also failed with exit 12/255. Publishing aborts on the first file failure; later streams are not confirmed copied. Failed book chunks remain local; no remote copy was verified. No credentials were read or changed.
- No capture data was added to Git. No code/config/crontab/service changes were made. Final coverage/pass-fail is not yet measurable; capture is scheduled through 17 Nov 20:30Z.
