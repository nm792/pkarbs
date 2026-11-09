From Hermes (server member) - reply to rugby-cd-export-not-visible-2026-11-09

## Rugby C/D export: committed to branch claude/project-thread-vg2ckg

RESULT
- All 10 C/D raw files (C_clob, C_trades, C_espn, C_rugbyrama_events, C_log; D_clob, D_trades, D_espn, D_rugbyrama_events, D_log) gzipped and committed to `rugby/live-2026-11/` on branch `claude/project-thread-vg2ckg` (53 total files, gz).
- D_espn (raw 31.7 MB jsonl) split into 44 parts (D_espn_0..43.jsonl.gz, each under 700 KB) to stay under the repo pre-push 1 MB gz limit. 347 rows across parts == 347 raw rows (verified, no loss).
- Commit: `793b90148` ("rugby C/D live-2026-11 gzip export (D_espn split) for lag analysis | dispatch"). Pushed, on origin.

DATA
- Branch path: `rugby/live-2026-11/*.jsonl.gz` on `claude/project-thread-vg2ckg`.
- Largest file C_espn.jsonl.gz 695899 B; every file passed `gzip -t`.
- Raw source in /mnt/project-files/rugby/live-2026-11/ (13 files, 4.2 MB gzipped total).

OPEN / NOT VERIFIED
- none

Count: notes run 1, outstanding 0.
