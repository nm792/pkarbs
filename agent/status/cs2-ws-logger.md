# Status: cs2-ws-logger — RUNNING, copy refreshed 17:17Z
**State:** RUNNING (transient `cs2-logger.service`, node pid 426344 etime >10h + watchdog 1533833). Last heartbeat 2026-11-04T17:17Z.
**Newest recv (raw):** `wc -l cs2_frames.jsonl` = 131,833; tail recv_iso ~17:16Z (fresh). Raw ps: `node /root/cs2logger/logger.js`, `/bin/bash watchdog.sh`.
**Hourly copy pushed 17:17Z:** cs2_frames.jsonl.gz (1.97 MB), cs2_changes.jsonl.gz (0.69 MB), logger.log.gz → `rn1/scores/cs2/server-2026-11/` on claude/project-thread-vg2ckg.
**Retention / stop:** per inbox 2026-11-04-stop-cs2-logger-after-nba — logger + watchdog stay up until NBA capture ends **06:45Z 5 Nov**, then stop watchdog first, logger second, move /root/cs2logger/out/ to the storage box. Do not restart after 06:45Z.
**Errors:** none. **waiting for Nick:** none.
