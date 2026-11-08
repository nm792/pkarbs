# outbox/2026-11-04-cs2-pilot-dryrun — CS2 pilot dry run STARTED

CS2 pilot dry run started 2026-11-04T07:17Z (prior round); confirmed live this round 07:47Z.

- Process: `/root/cs2pilot/venv/bin/python pilot.py --mode dry --out /root/cs2pilot/out --hours 14`, pid 50337, MemoryMax 512M, timeout 50400s. single process.
- Geoblock (start row of pilot.jsonl): country FI, `blocked: false`. Server passes Polymarket region check (live can run here). IP redacted.
- summary.json 07:46Z: games 2, live_games 2, halted false, positions 0, fills 0.
- report.py interim (111 log rows, 07:17Z–07:43Z): gates 3/6 — PASS geoblock, PASS no-bid-at/above-best-ask, PASS no crash; FAIL (early) >=20 round events (7), >=10 windows (2), feed-delay n>=10 (n=6). Full 6/6 evaluation at end of the 14 h run.
- No key installed, no LIVE_OK created (Nick's own steps). No orders sent (dry).

See agent/status/cs2-pilot.md for full state.
