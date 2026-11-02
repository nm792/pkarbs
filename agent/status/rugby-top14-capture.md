# Status: rugby Top 14 capture (task TASK-rugby-top14-capture-2026-11-07)

state: PREPARED — harness built, connectivity proven; windows scheduled 7-8 Nov
last agent write: 2026-11-02 16:03:10 UTC (window resolution outbox reply + this status; pushed)

- Task: agent/tasks/TASK-rugby-top14-capture-2026-11-07.md (config: agent/tasks/rugby-top14-config-2026-11-07.json).
- Harness: agent/tasks/rugby-top14-capture.py (one bounded process per window; MemoryMax 600M, swap 0, timeout 10500).
- CLOB market WS: CONNECTS from the server (verified this run; was 403 from the sandbox). Stream = price clock.
- Sports WS: connects; 0 rutopft currently (off-hours). ESPN 270559 is the cross-check / score clock if no rugby msgs.
- Windows (bounded, in-repo, one at a time, no P&L):
  - AB: 7 Nov 13:15-18:05 UTC, 6 matches, 36 tokens, nice -n 19, 600M cap, 18000s (merged; Nick approved)
  - D: 8 Nov 13:45-16:30 UTC, Vannes v Bordeaux (Rugbyrama 61243, 14:00 UTC), 6 tokens
  - C: 8 Nov 19:50-22:35 UTC, La Rochelle v Bayonne (Rugbyrama 61238, 20:05 UTC), 6 tokens
  - Each starts only after the prior is reviewed and its process is gone; AB waits on the coordinator re-check of gamma times 6 Nov.
- Outputs: rugby/<win>_{sports,clob,espn,trades}.jsonl + _log.txt; 10-min copy to /mnt/project-files/rugby/live-2026-11/.
- History: nudge 15:24Z 2 Nov -> picked up 2 Nov (connectivity proven, harness built).
- Next: run window A 7 Nov 13:15Z (systemd-run wrapper), status line every ~10 min in-window.
