# status: cs2-ws-logger

state: RUNNING
last_heartbeat: 2026-11-02 06:50Z
errors: none
output:
- raw: /root/cs2logger/out/cs2_frames.jsonl (streamed, receive-time stamped)
- changes: /root/cs2logger/out/cs2_changes.jsonl
- log: /root/cs2logger/out/logger.log
run:
- scope cs2-logger.scope (systemd-run, MemoryMax=512M, MemorySwapMax=0), timeout 43200, node v22, ws 8.22.1 (NODE_PATH=/root/ws_probe/node_modules)
- watchdog: ONE instance (proc via watchdog.sh, run.flag set)
- connected open #0 at 06:49:19Z; first frame gameId 1761578 PARIVISION-G2 score '4-2|0-1|Bo3' (rounds-in-map|map-wins|format) period 2/3 running
- output copied to /root/cs2logger/out only; repo copy of raw output next at status interval per task step 2
serviced_by: server agent (Hermes), Nick-approved 2 Nov 05:02Z, no further Nick needed for this start
