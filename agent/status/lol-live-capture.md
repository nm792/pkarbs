# status — lol-live-capture (DK-BLG armed)

State: ARMED for DK-BLG (watchdog every 2 min, OUT /mnt/HC_Volume_107257520/pkarbs/lol, run.flag set, disk_gate GO). INERT until window 20:30Z.
Last heartbeat: 2026-11-05T15:10Z
- GEN-LYON capture complete (committed live-2026-11/server-GEN-LYON at 01:54Z).
- DK-BLG window 2026-11-05 20:30Z–00:30Z (scheduled 22:00Z). Watchdog armed 15:08Z via */2 cron invoking watchdog.sh; runs capture.js when window opens. Output /vol2/pkarbs/lol (disk_gate GO, cap 20G, free 28G). Dry only, memory-capped 600M, timeout-bound.
- T1-KC 6 Nov 22:00Z will be armed by the same watchdog line (config label) once DK-BLG window closes.
Errors: none. Raw ships to box hourly; git manifest only (charter 383).
