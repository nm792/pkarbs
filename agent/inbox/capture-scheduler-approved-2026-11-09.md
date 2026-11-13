# Capture scheduler: APPROVED by Nick (9 Nov 00:19:32Z)

Decision card: "Install timers so future rugby and chess captures start themselves?" Nick chose "Yes, install and add rows".

Do this in your next round:
1. Add `python3 agent/tasks/schedule_captures.py --run-due` to your round (no systemd needed). It launches entries in `agent/tasks/captures-schedule.json` once, at kickoff minus lead_min, after the token check in `capture_launcher.py`.
2. After each launch, copy `/root/pkarbs/schedule/last_launch.txt` into `agent/status/rugby-top14-capture.md`.
3. Reply in `agent/outbox/capture-scheduler-approved-2026-11-09.md` with: pulled files OK, `--list` output, and one `--dry-launch` result.

Rows: none yet. They will be added to `captures-schedule.json` as soon as the next Top 14 windows and the chess World Championship game times are known.
