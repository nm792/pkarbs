# agent/outbox/2026-11-05-lol-pilot-start-2145Z.md

LoL pilot dry run started 2026-11-05T21:47:30Z for DK vs BLG (match 22:00Z, 5 Nov).

- Tests: test_lol_pilot.py 22/22 PASS (replay skipped — files absent, still pre-match 30s book window ok).
- Process: systemd-run --scope --unit=lol-pilot, /root/cs2pilot/venv/bin/python lol_pilot.py --mode dry --out /root/lolpilot/out --hours 8; pid 1559461, MemoryMax 512M, timeout 28800.
- Live check: geoblock blocked:false; discovered gid 1711013 "LoL: Dplus KIA vs Bilibili Gaming (BO5) - Worlds Playoffs" start 2026-11-05T22:00:00Z. summary.json: games 1, fills 0, positions 0.
- Out: /root/lolpilot/out/books.jsonl + pilot.jsonl (growing), summary.json, stdout.log.
- DRY ONLY confirmed: no LIVE_OK, no --mode live, key not used.
- Hourly: will copy pilot.jsonl + books.jsonl gzipped + summary.json to live/lol_pilot/runs/2026-11-05/ and commit.
- status: agent/status/lol-pilot.md.

Report output pending; speed_report.py + report.py run after first kill window / at first hourly copy.
