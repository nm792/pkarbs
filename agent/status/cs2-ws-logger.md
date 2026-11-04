# Status: cs2-ws-logger — RUNNING, copy refreshed 14:48Z

**State:** RUNNING (transient `cs2-logger.service`, node pid 426344 etime 04:40:00 + watchdog 1533833 etime 2-02:01). Last heartbeat 2026-11-04T14:48Z.
**Newest recv (raw):** `wc -l cs2_frames.jsonl` = 124,367; tail recv_iso **2026-11-04T14:48:16.998Z** (fresh). Raw ps: `426344 node /root/cs2logger/logger.js`, `1533833 /bin/bash watchdog.sh`.
**Hourly copy refreshed (14:48Z):** cs2_frames.jsonl.gz (2.07 MB), cs2_changes.jsonl.gz (727 KB), logger.log.gz → `rn1/scores/cs2/server-2026-11/`.
**Retention / stop:** per inbox 2026-11-04-stop-cs2-logger-after-nba — logger + watchdog stay up until NBA capture ends **06:45Z 5 Nov**, then stop watchdog first, logger second, move /root/cs2logger/out/ to the storage box. Do not restart after 06:45Z.
**Errors:** none. **waiting for Nick:** none.
