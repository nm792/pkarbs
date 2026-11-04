# Status: cs2-pilot (CS2 event-only pilot, phase 1 dry run)
**State:** STARTED 2026-11-04T07:17Z, RUNNING. Last heartbeat 2026-11-04T17:17Z UTC.
**Process:** pid 50337 — `/root/cs2pilot/venv/bin/python pilot.py --mode dry --out /root/cs2pilot/out --hours 14` (MemoryMax 512M, timeout 50400s). Source /tmp/cs2pilot-src. dry run must end ~21:17Z (14h).
**Geoblock (start row, pilot.jsonl):** country FI, `blocked: false`. Polymarket region check passes.
**summary.json (17:17Z):** dry run still live; positions 0, fills 0 (phase 1).
**report:** full 6-of-6 evaluation at end of the 14 h run (covers IEM Beijing 4–5 Nov).
**Hourly copy:** /root/cs2pilot/out/pilot.jsonl.gz (0.086 MB) + summary.json -> live/cs2_pilot/runs/2026-11-04-dry/ + commit. **17:17Z copy refreshed this round.**
**Errors:** none. **Stop:** `touch /root/cs2pilot/out/STOP`.
**waiting for Nick:** phase 2 (LIVE_OK) is Nick's own step, not started. Dry run remains read-only.
