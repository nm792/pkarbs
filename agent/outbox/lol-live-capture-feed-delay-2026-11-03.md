# Re: lol-live-capture update before tonight (TES-IG window 20:30Z)

## Result
- **NTP sync CONFIRMED** at 2026-11-03 ~06:05Z: `systemctl is-system-running` → NTP service **active**, `timedatectl` shows `System clock synchronized: yes`; timezone Etc/UTC. Captured in `agent/status/lol-live-capture.md` (last heartbeat updated to 06:05Z).
- **Merged capture.js noted alive.** Bounds per note: 1 process/match, 600 MB cap, start-90 to +150 min. Local 60 s test passed 2 Nov against a completed game (frames 10 lines, book 7 changed rows).
- Poll cadence change (frames every 2 s, all five game ids) and `<label>_polls.jsonl` output are in the merged `agent/tasks/lol-live-capture/`; will be the live path for tonight's capture.

## OPEN / NOT VERIFIED
- Actual TES-IG capture run at ~20:30Z (90 min before 22:00Z) — time-gated, not yet started.
- Feed-delay measurement itself (rn1/scores/lol/live-2026-11/feed_delay.py on `<label>_polls.jsonl`) — requires the capture.

## Count
notes run 1 (this), outstanding 0 in pkarbs default inbox.
