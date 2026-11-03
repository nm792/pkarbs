# Status: CS2 WS Logger (pkarbs)

state: RUNNING (watchdog-respawned node, no restart needed)
last_heartbeat: 2026-11-03 10:18Z (committed copy refreshed to live tail)
errors: none (count mismatch resolved 03:04Z)

## 3 Nov 2026
- systemd unit cs2-logger.service ActiveState=failed, ExecMainStartTimestamp 02 Nov 14:10:02Z (timeout-43200 run; NRestarts=0). Watchdog (bash /root/cs2logger/watchdog.sh pid 1533833, tracked bg job, not systemd) respawned logger: PID 3497389 `node /root/cs2logger/logger.js` ~02:11:12Z; VmRSS ~56 MB; keep-all; MemoryMax=512M/MemorySwapMax=0. Gap ~70 s. No config change.
- Committed copies (authoritative, refreshed 10:18Z): cs2_frames.jsonl.gz 58,774 lines / newest 10:18:28.952Z; cs2_changes.jsonl.gz 21,640; logger.log.gz 12. gzip -t OK.
- Reply on outbox/2026-11-03-cs2-logger-restart-proof.md (inbox answered in repo, no restart needed) and outbox/2026-11-03-cs2-count-mismatch.md (count corrected to 3,661 >=02:10Z on committed file).
output: raw /root/cs2logger/out/* (live, append-only); repo rn1/scores/cs2/server-2026-11/
