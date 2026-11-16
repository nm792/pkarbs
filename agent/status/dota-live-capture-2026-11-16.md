# status dota-live-capture (16-17 Nov 2026)

**State:** STARTED 2026-11-16T06:26:55Z; transient service `dotacap-2026-11-16.service` active at 07:32Z, Node PID 1700948 (timeout PID 1700947).
**Window:** 2026-11-16T08:30:00Z .. 2026-11-17T20:30:00Z; process waits for the scheduled start.
**Memory cap:** 400 MiB, swap cap 0; service reported active/running.
**Clock:** NTP synchronized (`yes`).
**Output:** on the data volume; at 07:32Z `capture.log` was 192 bytes and recorded the wait until 08:30Z. No match or book rows exist yet.
**30-minute copies:** NOT INSTALLED. No Dota publisher line was in the Prime crontab. The IT-approved publisher requires a new cron line; this scheduled run's delivery instruction prohibits creating/updating cron jobs, so it was not installed. No recurring copy/push will run from this session, and no repo data copy has been made.
**Errors:** none observed at startup. Capture has not reached 08:30Z; source reachability and pass criteria are not measured.
**Revert/cleanup:** no changes made to the running capture. The service manager can terminate `dotacap-2026-11-16.service`; captured output remains on the data volume.
