# Status: cs2-ws-logger — RUNNING, copy refreshed 13:50Z

**State:** RUNNING (transient `cs2-logger.service`, node pid 426344 + watchdog 1533833). Last heartbeat 2026-11-04T13:50Z.
**Newest recv:** cs2_frames.jsonl tail 2026-11-04T13:50:30Z (fresh, healthy — no restart needed this round).
**Hourly copy refreshed this round (13:50Z):** cs2_frames.jsonl.gz + cs2_changes.jsonl.gz + logger.log.gz → `rn1/scores/cs2/server-2026-11/`, committed.
**Retention / stop:** per inbox 2026-11-04-stop-cs2-logger-after-nba — logger + watchdog stay up until NBA capture ends **06:45Z 5 Nov**, then stop watchdog first, logger second, move /root/cs2logger/out/ to the storage box. Do not restart after 06:45Z.
**Errors:** none. **waiting for Nick:** none — stop is already Nick-approved (06:43Z).
