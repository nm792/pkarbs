# TASK (Hermes): scheduled capture launcher, dry run now; install only after Nick approves (card in the thread)

From: Claude, PK arbs rugby thread (coordinator asked). Window C (8 Nov) was missed because launches are manual.

New files in agent/tasks/: `capture_launcher.py` (timer-fired: checks tokens and REST books, launches the capture detached, re-checks after 60 s, logs to /root/pkarbs/schedule/launcher.log and last_launch.txt), `schedule_captures.py` (turns captures-schedule.json entries into one systemd timer each, firing at kickoff minus 15 min), `captures-schedule.json` (empty; add a row per window).
Tested here with stub captures: PASS path, bad-config FAIL path (no launch), dry run printing the systemd-run commands.

1. Now, read-only: `cd /root/pkarbs && python3 agent/tasks/capture_launcher.py rugby --window C --dry-launch` and `python3 agent/tasks/schedule_captures.py --list`. Paste both outputs in agent/outbox/capture-scheduler-2026-11-08.md. Also tell me whether `systemd-run --on-calendar` works on your box (`systemd-run --on-active=30 --unit=pkarbs-cap-selftest /bin/true`, then `systemctl list-timers pkarbs-cap-*`, then `systemctl stop pkarbs-cap-selftest.timer`).
2. Do NOT run `--install` or add schedule rows until Nick approves. Transient timers do not survive a reboot (see hermes-outages); after any reboot re-run `schedule_captures.py --install` (safe to repeat).
3. For the chess capture: tell me the next game start times you know, so I can add rows.
