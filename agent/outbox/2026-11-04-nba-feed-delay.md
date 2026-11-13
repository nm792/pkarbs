# outbox/2026-11-04-nba-feed-delay — NBA feed-delay capture STARTED

Capture started 2026-11-04T07:17Z (prior round); confirmed live this round 07:47Z.

- Process: `python3 poll.py /root/nbacap/out-2026-11-05 2026-11-04T23:50:00Z 2026-11-05T06:45:00Z`, pid 51008, MemoryMax 300M, timeout 27000s. single process, stdlib.
- It sleeps on its own until 23:50Z by design (per task file); output files present (empty until games start 5 Nov 00:00Z).
- cs2-ws-logger (Polymarket side, NBA frames) confirmed running.
- First check 00:15Z: `tail log.jsonl; wc -l *.jsonl`; kill on 403/429 storm. Copy to winmodels/raw/nbacap-2026-11-05/ every 30 min.

See agent/status/nba-feed-delay.md.
