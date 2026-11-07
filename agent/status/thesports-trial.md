# status: thesports-trial (TASK-thesports-trial-2026-11-05)

- **RECORDER STOPPED, not running (2026-11-07T21:55Z check).** Only chunk `final-topics-32295` exists (vol /mnt/HC_Volume_107257520/pkarbs/thesports/). Last output written 16:00:08Z; capture.py not running; no systemd unit, no tmux session, no respawn cron guard.
- Stop was CLEAN (log tail): `mqtt_disconnect "Normal disconnection"` then `stop` @ ms 1794067213141 (≈16:00:13Z). Counts at stop: books 1,412,988 rows; ts_mqtt 528,438; pmws 13,156; markets 197. No crash/error line.
- Cause of the 16:00Z stop not yet established (no guard would have respawned it). Capture was expected to continue (last outbox 11:04Z: "recording continues as-is; 2h export cadence").
- **This is a live capture outage during the priority 7-8 Nov CS2/LoL Worlds window. Restart of live/thesports/capture.py is a process restart = consent-gated, waits for Nick.**
- last_heartbeat: 2026-11-07T21:55Z
