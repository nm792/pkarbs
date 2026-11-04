# Status: nba-feed-delay (live NBA feed-delay capture, night 4–5 Nov)

**State:** STARTED 2026-11-04T07:17Z, WAITING-for-window (sleeps until 23:50Z by design). Last heartbeat 2026-11-04T07:47Z UTC.
**Process:** pid 51008 — `python3 poll.py /root/nbacap/out-2026-11-05 2026-11-04T23:50:00Z 2026-11-05T06:45:00Z` (MemoryMax 300M, timeout 27000s). single process, stdlib only.
**Window:** captures 5 Nov 00:00Z–03:30Z games; poll exits 06:45Z. cs2-ws-logger carries the Polymarket side (NBA frames) through 06:45Z.
**Output:** /root/nbacap/out-2026-11-05/ (empty until games start). Copy every 30 min -> winmodels/raw/nbacap-2026-11-05/ (gzip, from-scratch never append).
**First check 00:15Z:** tail log.jsonl + wc -l *.jsonl; kill + report on 403/429 storm.
**Cleanup at end:** confirm python gone (ps, free -m). Owner thread does analysis.
**Errors:** none so far. **waiting for Nick:** none — read-only capture.
