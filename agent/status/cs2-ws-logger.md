# status: cs2-ws-logger

state: RUNNING (CS2-only capture) / keep-all-messages change WAITING-FOR-NICK
last_heartbeat: 2026-11-02 07:36Z
errors: none
output:
- raw: /root/cs2logger/out/cs2_frames.jsonl (streamed, receive-time stamped)
- changes: /root/cs2logger/out/cs2_changes.jsonl
- log: /root/cs2logger/out/logger.log
run:
- scope cs2-logger.scope (systemd-run, MemoryMax=512M, MemorySwapMax=0), timeout 43200, node v22, ws 8.22.1 (NODE_PATH=/root/ws_probe/node_modules)
- watchdog: ONE instance (proc via watchdog.sh, run.flag set)
- live logger.js == repo-reviewed version (byte-identical)
- connected open #0 at 06:49:19Z; 178 CS2 frames as of 07:31Z
serviced_by: server agent (Hermes), Nick-approved 2 Nov 05:02Z
waiting_for_nick:
- 2026-11-02-ws-keep-all-messages: keeping ALL sports-WS messages (incl cricket NPL 3 Nov) needs edit to logger.js:24 (drop '!== cs2' guard) + restart of cs2-logger.scope. Both are Nick-gated (code edit + restart). Not applied; held per note's own 'tell us first'. Reply in agent/outbox/2026-11-02-ws-keep-all-messages.md.
