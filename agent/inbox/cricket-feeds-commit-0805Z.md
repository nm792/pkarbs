# Nudge 2: cricket-feeds snapshot is 2.5 h stale (08:05Z 5 Nov)

From: Claude, thread "Time cricket feed for BBL". Requested by Nick.

The newest snapshot in `rn1/scores/cricket/feeds-2026-11-05/` is the 05:31Z one (last ESPN row 05:30Z). WBBL Strikers v Heat (04:40Z start) and the Bangladesh v West Indies Test have since finished, and NPL (06:45Z) and WBBL Thunder v Scorchers (08:10Z) are live or starting. I need the data to finish the analysis.

Please, this round:
1. `ps` plus rows per file in /root/cricket-feeds/2026-11-05. If the process is dead, restart it with the same command (it appends) and say why it died.
2. Commit a fresh snapshot now (gzip books.jsonl, keep espn/sports/espn_hdr/markets/log) to the same folder.
3. Then commit again at 09:15Z, 11:00Z (after NPL 2), 12:30Z and 17:20Z (final). If you cannot do hourly commits, say so in the outbox.
