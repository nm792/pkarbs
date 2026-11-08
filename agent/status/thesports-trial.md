# status: thesports-trial (TASK-thesports-trial-2026-11-05)

- **RECORDER STOPPED, not running (2026-11-07T21:55Z check).** Only chunk `final-topics-32295` exists (vol /mnt/HC_Volume_107257520/pkarbs/thesports/). Last output written 16:00:08Z; capture.py not running; no systemd unit, no tmux session, no respawn cron guard.
- Stop was CLEAN (log tail): `mqtt_disconnect "Normal disconnection"` then `stop` @ ms 1794067213141 (≈16:00:13Z). Counts at stop: books 1,412,988 rows; ts_mqtt 528,438; pmws 13,156; markets 197. No crash/error line.
- Cause of the 16:00Z stop not yet established (no guard would have respawned it). Capture was expected to continue (last outbox 11:04Z: "recording continues as-is; 2h export cadence").
- **This is a live capture outage during the priority 7-8 Nov CS2/LoL Worlds window. Restart of live/thesports/capture.py is a process restart = consent-gated, waits for Nick.**
- last_heartbeat: 2026-11-07T21:55Z

- **RECORDER RESTARTED RUNNING (2026-11-08T00:11Z — Nick-approved, executed).** Relaunch via start_writer.sh (`thesports-capture-b`, gate_rc=0) into new chunk `final-topics-32295b` (spool /mnt/HC_Volume_107257520/pkarbs/thesports/). Process live since 00:21Z (pid 2791157/2791163). Fresh books.jsonl 22,754 rows @ 00:31Z; pmws 333; share/ gz current 00:31Z. Single instance confirmed. Outbox `thesports-restart-approved-2026-11-08.md` RAN filed.
- 11:02Z–16:00Z gap slim export + standing 2h export cadence: follow-on task (export task), to be committed per thesports export protocol.
- last_heartbeat: 2026-11-08T00:31Z
