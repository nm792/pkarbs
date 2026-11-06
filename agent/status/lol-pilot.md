# agent/status/lol-pilot.md — LoL pilot dry run (DK vs BLG, 5 Nov 22:00Z)

State: RUNNING (dry) — started 2026-11-05T21:47:30Z
Pid: 1559461 (timeout 28800, MemoryMax 512M)
Out: /root/lolpilot/out (books.jsonl, pilot.jsonl, summary.json, stdout.log)
Tests: test_lol_pilot.py 22/22 PASS (replay skipped, files absent)
Launched: systemd-run --scope --unit=lol-pilot -- MemoryMax=512M timeout 28800 lol_pilot.py --mode dry --hours 8

Start line (pilot.jsonl): geoblock blocked:false (FI), discover gid 1711013 "LoL: Dplus KIA vs Bilibili Gaming (BO5) - Worlds Playoffs" start 2026-11-05T22:00:00Z.
summary.json at start: games 1, live_games 0, fills 0, positions 0, realized 0.

DRY ONLY: no LIVE_OK, no --mode live, key unused (note 154 + task lol-pilot.md).
Match cap 8h (to ~05:47Z 6 Nov); repeats 6 Nov 21:30Z T1 vs KC same out folder.
Last heartbeat: 2026-11-05T21:47Z
Output paths: /root/lolpilot/out/; hourly copies to live/lol_pilot/runs/2026-11-05/ (gzipped).
