## Gas waiter install (20 Nov)

- Code source: `0e113601dc1bad5a763b318044c9066002ce5ae6` on `claude/project-thread-lfb1pf`; exported to `/mnt/HC_Volume_107257520/pkarbs/deploy/gas-0e113601`.
- Tests on the exact source: `test_wait_listing.py` — 2 of 2 pass; `test_pm_gas_trades.py` — 2 of 2 pass; `test_gate_boundary.py` — 5 of 5 pass. The two simulated poll-reset messages were expected test cases; each suite passed.
- VOL2 free space at install check: 11,302,965,248 bytes (above the 10 GB floor). Output directory `/mnt/HC_Volume_107257520/gas` exists.
- Installed Prime crontab entry: `50 14 20 11 * cd /mnt/HC_Volume_107257520/pkarbs/deploy/gas-0e113601 && python3 scan/gas_window/wait_listing.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --wait-until 2026-11-20T16:30:00Z --record-seconds 5400 > /mnt/HC_Volume_107257520/gas/wait-20261121.log 2>&1`.
- The one-shot is scheduled for 14:50Z today. The waiter has not run yet; PID, listing detection and output growth are not yet verified.
