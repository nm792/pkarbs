# status dota-live-capture (16-17 Nov 2026)

**State:** STARTED 2026-11-16T06:26:55Z; transient systemd service `dotacap-2026-11-16.service` active, PID 1700948 (Node child; timeout PID 1700947).
**Window:** 2026-11-16T08:30:00Z .. 2026-11-17T20:30:00Z; process waits for the scheduled start.
**Memory cap:** 400 MiB, swap cap 0; systemd reports active/running.
**Clock:** NTP synchronized (`yes`).
**Source/config:** task commit daf1447d; capture.js and config.json checked; 14 series, 42 markets. SHA-256: capture.js `918913fe9e13d9bcbb8b81d5e0255531321bd7632267d058800aea71a4e87994`; config.json `aa2dc973e10101a268aec7faef8dd26c0f6da342f2a8e5b85cee39ae2d1f1a85`.
**Output:** `/mnt/HC_Volume_107257520/pkarbs/dotacap/run-2026-11-16/out/` on the data volume.
**30-minute copies:** NOT INSTALLED. No existing Dota copy/push runner or matching cron line was present. The required recurring publisher needs a new runner/configuration change; this run has not installed it. No repository data copy has been made.
**Errors:** none observed at startup. Capture has not reached 08:30Z; source reachability and pass criteria are not yet measured.
**Revert/cleanup:** use the service manager to terminate `dotacap-2026-11-16.service`; output retained on the data volume.
