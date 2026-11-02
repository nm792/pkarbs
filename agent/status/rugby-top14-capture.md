# Status: rugby Top 14 capture (task TASK-rugby-top14-capture-2026-11-07)

state: PREPARED — harness built, connectivity proven; windows scheduled 7-8 Nov
last agent write: 2 Nov ~15:3xZ (outbox reply + this status; pushed)

- Task: agent/tasks/TASK-rugby-top14-capture-2026-11-07.md (config: agent/tasks/rugby-top14-config-2026-11-07.json).
- Harness: agent/tasks/rugby-top14-capture.py (one bounded process per window; MemoryMax 600M, swap 0, timeout 10500).
- CLOB market WS: CONNECTS from the server (verified this run; was 403 from the sandbox). Stream = price clock.
- Sports WS: connects; 0 rutopft currently (off-hours). ESPN 270559 is the cross-check / score clock if no rugby msgs.
- Windows (bounded, in-repo, no P&L):
  - A: 7 Nov 13:15-15:45 UTC — RC Vannes v Bordeaux (1 match, 6 tokens)
  - B: 7 Nov 15:20-18:00 UTC — 5 matches, 30 tokens
  - C: 8 Nov 19:50-22:30 UTC — La Rochelle v Bayonne (6 tokens)
  - Each starts only after the prior is reviewed and its process is gone.
- Outputs: rugby/<win>_{sports,clob,espn,trades}.jsonl + _log.txt; 10-min copy to /mnt/project-files/rugby/live-2026-11/.
- History: nudge 15:24Z 2 Nov -> picked up 2 Nov (connectivity proven, harness built).
- Next: run window A 7 Nov 13:15Z (systemd-run wrapper), status line every ~10 min in-window.
