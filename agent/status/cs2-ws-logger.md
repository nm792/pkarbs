# Status: cs2-ws-logger — RUNNING, copy refreshed 13:10Z

**State:** RUNNING (transient `cs2-logger.service`, node pid 426344 + watchdog 1533833). Last heartbeat 2026-11-04T13:10Z.
**Newest recv:** cs2_frames.jsonl tail 2026-11-04 ~13:08Z (fresh). frames growing (29.6 MB raw).
**Hourly copy refreshed this round (13:10Z):** cs2_frames.jsonl.gz + cs2_changes.jsonl.gz + logger.log.gz → `rn1/scores/cs2/server-2026-11/`, committed.
**Retention / stop:** per inbox 2026-11-04-stop-cs2-logger-after-nba — logger + watchdog stay up until NBA capture ends **06:45Z 5 Nov** (covers the Polymarket side of the NBA feed-delay test), then stop watchdog first, logger second, and move /root/cs2logger/out/ to the storage box (storage-offload ruling). Do not restart after 06:45Z (restart once if the 12 h timeout ends before then so the NBA window stays covered).
**Errors:** none. **waiting for Nick:** none — stop is already Nick-approved (06:43Z).
