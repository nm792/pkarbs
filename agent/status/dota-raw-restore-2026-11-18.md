# P28a — Dota raw capture location, 2026-11-18

- R1 local output: YES. `/vol2/pkarbs/dotacap/run-2026-11-16/out/` contains six JSONL files; line counts: books 107,624; league_games 15,904; opendota_live 2,723; realtime 145,268; rt_polls 325,064; sportsws 7,158; total 603,741. Directory size: 332,635,977 bytes.
- R2 local chunks: YES. `publisher/chunks/` contains 75 files, 49,194,725 bytes. The current chunk names differ from the 75 historical manifest names; the publisher removes chunks after shipping. The manifest records 75 historical rows.
- R3 storage box: YES. `pkarbs/dotacap-2026-11-16/` lists 75 files, 15,650,708 bytes. Downloaded a temporary read-only copy and checked each manifest SHA-256: 75 checked, 0 missing, 0 failed.
- R4 other-copy search: NOT RUN; the task required it only if R1–R3 all failed.
- P28b: ran the specified lag analysis on R1 data, using the config extracted from the fetched origin branch. It completed with exit 0 under a 2,000 MiB memory cap; output paths: `winmodels/dota/livelag/out_lag_2026-11-16.json` and `.txt`. The repeated run completed in 22.95 s, peak RSS 1,642,256 KiB. A prior 1,500 MiB attempt was OOM-killed; the successful 2,000 MiB rerun is the recorded result.
- No capture data was moved, deleted, or restored; no code/config was changed. P28a/P28b reply: `agent/outbox/2026-11-18-dota-raw-restore.md`.
