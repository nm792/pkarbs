# Status: cs2-ws-logger — RUNNING, copy refreshed 16:16Z
**State:** RUNNING (transient `cs2-logger.service`, node pid 426344 etime >5h + watchdog 1533833). Last heartbeat 2026-11-04T16:16Z.
**Newest recv (raw):** `wc -l cs2_frames.jsonl` = 128,554; tail recv_iso ~16:16Z (fresh). Raw ps: `node /root/cs2logger/logger.js`, `/bin/bash watchdog.sh`.
**Hourly copy pushed 16:16Z:** cs2_frames.jsonl.gz (2.1 MB), cs2_changes.jsonl.gz (0.7 MB), logger.log.gz → `rn1/scores/cs2/server-2026-11/` on claude/project-thread-vg2ckg (commit 66746921).
**Retention / stop:** per inbox 2026-11-04-stop-cs2-logger-after-nba — logger + watchdog stay up until NBA capture ends **06:45Z 5 Nov**, then stop watchdog first, logger second, move /root/cs2logger/out/ to the storage box. Do not restart after 06:45Z.
**Errors:** none. **waiting for Nick:** none.
