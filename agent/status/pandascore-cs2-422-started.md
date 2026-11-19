# P41 CS2 #422 run — started checkpoint

- Start UTC: 2026-11-19T00:18:44Z.
- Code base: `d93c3bbdfe599b7c738c6cc2f2fbf0c5398228df` (`claude/project-thread-vg2ckg`).
- Runner: reviewer-signed `run_cs2_422.sh`, running from the clean export under the data volume; process 2471704, plain scorer process 2473255 observed alive at 00:28:16Z.
- `agent/status/pandascore-cs2-422-pmdirs.log` records the discovered PM directories and start time.
- Plain scorer is still running; no result JSON yet. Its log currently reports unreadable partial gzip inputs: `pandascore_2026111612.jsonl.gz` (invalid block type) and the still-open `pandascore_2026111823.jsonl.gz` (EOF before end marker). These are logged by the scorer; no source data was modified.
- At 00:33:48Z the plain scorer remained live (15m04s elapsed, RSS 67,004 KiB); no JSON output had appeared. Its log reported two partial/corrupt gzip inputs (one invalid block type; one open-file EOF). To honor the bounded-run limit, the exact runner and scorer PIDs were sent SIGTERM at 00:33:48Z and were absent at 00:33:50Z. No JSON result was produced and no scorer exit code was captured. The logs are preserved; no source data was changed. This is a partial run, not a CS2 result. Reviewer chunking/re-scope is needed before another attempt; the reviewer note said it would fix script issues within 30 minutes if it failed.
