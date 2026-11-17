# Dota 2 live capture — update 02:45Z, 17 Nov

- Capture is still active (timeout PID 1700947; Node PID 1700948; start 16 Nov 06:26:55Z). **CRITICAL: the 90,000-second timeout reaches 17 Nov about 07:26:55Z, before the configured 20:30Z end.** I left the running process unchanged.
- At 02:43Z, rows: books 107,624 (last write 22:59Z), league_games 12,595, opendota_live 2,161, realtime 116,879, rt_polls 260,859, sportsws 7,123 (last write 23:29Z). There are 497 league-query errors; the latest is a null `games` response at 02:40Z. Final in-game-minute coverage and the 80% pass thresholds are not measured.
- Scheduled box publication still fails with authentication errors. Manual invocation of the existing publisher at 02:42Z transferred and checksum-verified five deltas; manifest is 75 chunks / 562,819 rows, pushed at `53daee4ac232962914b78668dd1d3f2aa8acddb5`. No credential values were read; no code or crontab changes were made.
- The 30-minute publisher and 20:35Z final-copy/removal lines remain installed. Final copy has not fired. Evidence: `manifest/dotacap-2026-11-16.tsv`.
- Capture remains in progress; complete-window coverage and the pass/fail result are open. No restart was attempted.
