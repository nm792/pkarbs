## Gas waiter install (20 Nov)

- Target code: `0e113601dc1bad5a763b318044c9066002ce5ae6` on `claude/project-thread-lfb1pf`.
- Tests run from that exact commit: `test_wait_listing.py` — 2 of 2 pass; `test_pm_gas_trades.py` — 2 of 2 pass; `test_gate_boundary.py` — 5 of 5 pass.
- Install gate failed: VOL2 had 7,097,942,016 bytes free (about 6.61 GiB), below the task's 10 GB minimum. The waiter and crontab entry were not installed; no recorder started and no data was written.
- Output was extracted to the alternate mounted volume for tests because `/tmp` was full. No source files were edited.
- State: waiting for VOL2 free space to reach at least 10 GB; no further check in this session.
