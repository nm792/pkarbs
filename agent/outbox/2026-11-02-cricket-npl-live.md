# Outbox: Nepal PL live capture — pickup confirmed (dry run PASS)

From: Hermes (server member). Replying to agent/inbox/2026-11-02-cricket-npl-live.md (2 Nov 15:30Z).

## Pickup — confirmed before 06:00Z 3 Nov deadline
Dry run per the inbox (`--minutes 0.2` on id 1558592, yesterday's match), run 2 Nov 15:47Z:
- **polls 3, empty_polls 0, rows 7**, **exit 0**.
- Rows are real ball-by-ball events (over 15.4→16.4, plays run/six/four/no-run; e.g. "Khanal to Aarif Sheikh, 1 run", "Khanal to Rutherford, SIX").
- Output: `agent/status/cricket-npl-live.md` + `/root/cricket-live/dryrun/cricket_1558592_20261102T1547Z.jsonl` (copied to `/root/cricket-live/share/`).

Feed connects, 0 empty polls over the dry window; logger is healthy for the live run.

## Windows (per task spec, one process each, never overlapping) — scheduled
- **A** id 1558593 Biratnagar Kings v Janakpur Bolts — run 3 Nov **06:30Z** (255 min), start minus 15 min.
- **B** id 1558594 Lumbini Lions v Pokhara Avengers — run 3 Nov **10:30Z** (255 min).
- Each: `systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 15600 python3 -m evrules.live_pbp_logger cricket <id> --minutes 255 --every 5 --out /root/cricket-live --share /root/cricket-live/share`.
- Window B starts 15 min before A's run ends; kill A first on result, confirm stopped.
- Data committed to `rn1/scores/cricket/live-2026-11-03/`; trades pulled after each match to `trades_<id>.json`.

## Waiting on Nick
- none for this task (no code change, no restart — protocol-compliant capture).
