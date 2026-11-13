# TASK (Hermes): confirm rugby window C launched, then export C data (read-only, small)

From: Claude, PK arbs rugby thread. Nick's analysis needs raw files; raw D/C jsonl only live on the server.

1. Now: did C launch at 19:50Z from the patched copy? Report `tokens=` log line, pid, and `wc -l rugby/C_clob.jsonl rugby/C_trades.jsonl` with C_clob rows by event_type. One line in agent/outbox/rugby-c-launch-and-export-2026-11-08.md. If C did NOT launch, say so and launch it now (Nick approved the patch and the windows; the kickoff was 20:05Z, so it is already live).
2. After C ends (~22:35Z): copy rugby/C_clob.jsonl, C_trades.jsonl, C_espn.jsonl, C_rugbyrama_events.jsonl and C_log.txt to /mnt/project-files/rugby/live-2026-11/ (these are small; the 1.3 GB Rugbyrama raw stays on the volume). Same for D_clob.jsonl, D_trades.jsonl, D_espn.jsonl, D_rugbyrama_events.jsonl, D_log.txt. Then commit nothing big; list the paths and sizes in the outbox note.
