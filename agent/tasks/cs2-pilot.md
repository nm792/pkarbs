# TASK: CS2 event-only pilot, phase 1 = DRY RUN on live markets (no key, no orders)

Nick approved building the capped CS2 live pilot on 4 Nov 2026 06:34Z. Code: `live/cs2_pilot/` (README there).
Phase 1 below needs no key and sends no orders. Phase 2 (live) is NOT part of this task: it starts only after Nick
reviews the dry-run report, installs the key himself (`live/cs2_pilot/KEY-INSTALL.md`) and writes `LIVE_OK` himself.

**Question:** does the pilot, run on the server against live tier-1 CS2 markets, see round events on time, place its
(paper) bids by the rule, and log queue position, feed delay and 1-minute markouts; and does the server pass
Polymarket's region check (needed before any live order)?

**Pass/fail, fixed before the run** (printed by `python3 report.py <out>/pilot.jsonl`):
1. geoblock check at start recorded with `"blocked": false` (if true: report it; live cannot run on this server)
2. >= 20 within-map round events on tier-1 matches
3. >= 10 bid windows opened
4. no paper bid at/above the best ask or above mid x 0.975
5. feed delay measured on >= 10 events
6. no crash (no `error` with where=main)
PASS = 6 of 6. On FAIL report the failing gates with examples. Do not report P&L as a result in either case.

**Run (PROTOCOL.md rules 1-6):**
```bash
cd <repo>/live/cs2_pilot && python3 test_pilot.py            # must print "30 of 30 tests pass"
python3 -m venv /root/cs2pilot/venv && /root/cs2pilot/venv/bin/pip install -q 'polymarket-client==0.16.0' 'websockets==15.0.1'
mkdir -p /root/cs2pilot/out
systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0 timeout 50400 \
  /root/cs2pilot/venv/bin/python pilot.py --mode dry --out /root/cs2pilot/out --hours 14 \
  >> /root/cs2pilot/out/stdout.log 2>&1 &
```
- Single process, 14 h cap (covers IEM Beijing play on 4-5 Nov), ~1 request/s to clob.polymarket.com plus trades
  polls only while a bid window is open. Needs outbound to gamma-api, clob, data-api, sports-api.polymarket.com and
  polymarket.com (geoblock check).
- Every hour: copy (do not append) `/root/cs2pilot/out/pilot.jsonl` gzipped plus `summary.json` to
  `live/cs2_pilot/runs/2026-11-04-dry/` and commit. Write `agent/status/cs2-pilot.md` with the `report.py` output.
- Stop early: `touch /root/cs2pilot/out/STOP`.

**Clean up (rule 4):** when done, confirm the process exited, report `ps` and `free -m`, keep the out folder (raw data).
