# Status: cs2-pilot (CS2 event-only pilot, phase 1 dry run)

**State:** STARTED 2026-11-04T07:17Z, RUNNING. Last heartbeat 2026-11-04T13:10Z UTC.
**Process:** pid 50337 — `/root/cs2pilot/venv/bin/python pilot.py --mode dry --out /root/cs2pilot/out --hours 14` (MemoryMax 512M, timeout 50400s). Source /tmp/cs2pilot-src.
**Geoblock (start row, pilot.jsonl):** country FI, `blocked: false`. Polymarket region check passes — live could run on this server. IP redacted.
**summary.json (13:07Z):** dry run still live; positions 0, fills 0 (phase 1).
**report:** full 6-of-6 evaluation at end of the 14 h run (covers IEM Beijing 4–5 Nov).
**Hourly copy:** /root/cs2pilot/out/pilot.jsonl.gz + summary.json -> live/cs2_pilot/runs/2026-11-04-dry/ + commit. **13:10Z copy refreshed this round.**
**Errors:** none. **Stop:** `touch /root/cs2pilot/out/STOP`.
**waiting for Nick:** key install verified workable (see outbox/cs2-session-key-verify.md); phase 2 (LIVE_OK) is Nick's own step, not started. Dry run remains read-only.
