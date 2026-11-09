# START NOW: LoL pilot DRY run for DK-BLG (match 22:00Z, 5 Nov)

Task file: `agent/tasks/lol-pilot.md` (merged earlier today; no ack or status from you yet). DRY ONLY: no LIVE_OK, no `--mode live`,
the key is not used (Nick 02:20Z: no real money until he has seen our speed).

Start as soon as you read this, even if after 22:00Z (the bot needs ~30 s of book history before the first kill):
```bash
cd <repo>/live/lol_pilot && python3 test_lol_pilot.py      # must end "24 of 24 tests pass"
mkdir -p /root/lolpilot/out
systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0 timeout 28800 \
  /root/cs2pilot/venv/bin/python lol_pilot.py --mode dry --out /root/lolpilot/out --hours 8 \
  >> /root/lolpilot/out/stdout.log 2>&1 &
```
Then write `agent/status/lol-pilot.md` (start time, pid, `ls -l /root/lolpilot/out/books.jsonl`), and copy pilot.jsonl + books.jsonl
gzipped to `live/lol_pilot/runs/2026-11-05/` hourly. Reply in `agent/outbox/2026-11-05-lol-pilot-start-2145Z.md`.
