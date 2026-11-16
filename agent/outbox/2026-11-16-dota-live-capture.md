# Dota live capture start — 16 Nov 2026

Capture started at 2026-11-16T06:26:55Z as `dotacap-2026-11-16.service`, a transient systemd service with a 400 MiB memory cap and no swap. Node PID 1700948 is active; it waits until 08:30Z, then captures through 20:30Z on 17 Nov. NTP reported synchronized. Output is on the data volume at `/mnt/HC_Volume_107257520/pkarbs/dotacap/run-2026-11-16/out/`.

The task's 30-minute gzip/repository-copy publisher was not installed: there was no existing runner or cron line, and adding one requires a new runner/configuration change. This blocker is recorded in the project's status; no capture rows exist yet because the window has not started. Status: `agent/status/dota-live-capture-2026-11-16.md`.
