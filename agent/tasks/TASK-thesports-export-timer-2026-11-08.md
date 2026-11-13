# TASK (HIGH PRIORITY): make the TheSports 2 h slim export run on a timer, not on the dispatcher (written 2026-11-08T05:25Z)

Standing instruction from Nick (7 Nov 07:38Z): "we need to assess this trial properly so keep the records". Nick approved the capture restart (8 Nov 00:00Z) and the export cadence. This task needs no further approval: it is routine, read-only for PM/TheSports, writes only to /vol and the repo.

Problem: the newest slim in the repo is `final-topics-32295b-slim`, ending 02:09Z. The 2 h export did not run at ~04:10Z. Your 03:05Z reply said the cadence "rides the existing dispatcher"; the dispatcher heartbeats continue (05:00Z) but `agent/status/thesports-trial.md` has not moved since 03:05Z, so the export step is not firing. The exporter has never run unattended since it was first created.

Do, in this order:
1. Export and commit the slim for `final-topics-32295b` from 02:09Z to now, same layout. Refresh `diary/*-2026-11-08.json` for new match ids.
2. Arm a real timer for this: a systemd timer or cron line (not dependent on Nick or on a thread) that every 2 h runs export_slim.py for the live chunk, commits to `claude/project-thread-vg2ckg` and updates `agent/status/thesports-trial.md` with the time and row counts. One instance only; respect the disk charter.
3. In `agent/outbox/thesports-export-timer-2026-11-08.md`, report: exporter error (if any) and why it stopped, the timer definition, the first timer-run time, and the time of the next export.
Priority: this blocks the signal-vs-noise analysis Nick is waiting on ("and?" 04:55Z).
