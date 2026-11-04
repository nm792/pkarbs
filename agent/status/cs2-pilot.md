# Status: cs2-pilot (CS2 event-only pilot, phase 1 dry run)

**State:** STARTED 2026-11-04T07:17Z, RUNNING. Last heartbeat 2026-11-04T07:47Z UTC.
**Process:** pid 50337 — `/root/cs2pilot/venv/bin/python pilot.py --mode dry --out /root/cs2pilot/out --hours 14` (MemoryMax 512M, timeout 50400s). Source /tmp/cs2pilot-src.
**Geoblock (start row, pilot.jsonl):** country FI, `blocked: false`. Polymarket region check passes — live could run on this server. IP redacted.
**summary.json (07:46Z):** games 2, live_games 2, halted false, positions 0, fills 0.
**report.py interim (07:17Z–07:43Z, 111 rows):** PASS geoblock / PASS no-bid at-or-above best ask / PASS no crash; FAIL(early) round-events 7/20, windows 2/10, feed-delay n 6/10. Full 6-of-6 evaluated at end of the 14 h run (covers IEM Beijing 4–5 Nov).
**Hourly copy:** /root/cs2pilot/out/pilot.jsonl.gz + summary.json -> live/cs2_pilot/runs/2026-11-04-dry/ + commit, each hour.
**Errors:** none. **Stop:** `touch /root/cs2pilot/out/STOP`.
**waiting for Nick:** none — dry run read-only; phase 2 (key+LIVE_OK) is Nick's own step, not started.
