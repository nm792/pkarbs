# P17a — Dota lag 16–17 Nov

- Result: NOT RUN. The exact requested lag.py command exited 1; it could not open `../../../agent/tasks/dota-live-capture-2026-11-16/config.json` (FileNotFoundError). A retry using the path depth implied by the current checkout also exited 1 because the capture directory `$HOME/dotacap/out-2026-11-16` is absent.
- Verified: task `config.json` exists on `origin/claude/project-thread-vg2ckg`, but not in the dirty working tree; capture input directory is absent at the specified location. No result JSON was created. No checkout/restore or capture recreation was attempted.
- Evidence: `winmodels/dota/livelag/out_lag_2026-11-16.txt` contains the exact error and missing-input finding.
- Requested reviewer action: confirm the intended capture/config paths or restore the missing capture input; then rerun Part A.
