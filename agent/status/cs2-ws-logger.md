# status: cs2-ws-logger

state: RUNNING (logger pid 3497389 alive; watchdog respawn active). Unit itself = failed (timeout 43200 hit 02:10Z) but watchdog keeps logger alive.
last_heartbeat: 2026-11-03 05:35Z (tail), committed copy refreshed 05:40Z
errors: none (count mismatch resolved 03:04Z)

## 3 Nov 2026
- systemd unit cs2-logger.service ActiveState=failed, ExecMainStartTimestamp 02 Nov 14:10:02Z (timeout-43200 run; NRestarts=0).
- Live logger PID 3497389 `node /root/cs2logger/logger.js`, watchdog respawned ~02:11:12Z; VmRSS ~56 MB; keep-all; MemoryMax=512M/MemorySwapMax=0. Gap ~70 s. No config change.
- Committed copies (authoritative, refreshed 05:40Z): cs2_frames.jsonl.gz 53,859 lines / newest 05:35:15.957Z; cs2_changes.jsonl.gz 20,772; logger.log.gz. gzip -t OK. Hourly copies continue while logger runs.
output: raw /root/cs2logger/out/* (live, append-only); repo rn1/scores/cs2/server-2026-11/
