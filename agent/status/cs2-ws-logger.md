# status: cs2-ws-logger

state: RUNNING (ALL sports-WS messages captured, incl. cricket) — keep-all applied 2 Nov 14:0xZ
last_heartbeat: 2026-11-02 14:50Z
errors: none
output:
- raw: /root/cs2logger/out/cs2_frames.jsonl (all leagues, per-line leagueAbbreviation tag; receive-time stamped)
- changes: /root/cs2logger/out/cs2_changes.jsonl
- log: /root/cs2logger/out/logger.log
run:
- service cs2-logger.service (systemd-run, MemoryMax=512M, MemorySwapMax=0, timeout 43200), node v22, ws 8.22.1 (NODE_PATH=/root/ws_probe/node_modules); ExecMainStartTimestamp=2026-11-02 14:10:02Z
- watchdog: RUNNING (pid 1533833, watchdog.sh), single.
- logger.js == repo version (byte-identical); guard at line 24 removed (all messages). Frame mix as of 14:48Z: cs2=2900, cricket=43, dota2=256, atp=225, mlbb=113, cbb=88, es2=41, ukr1=3.
serviced_by: server agent (Hermes), Nick-approved 2 Nov 05:02Z (task) + 14:35Z (edit+restart)
waiting_for_nick: none (cricket-capture-approved answered; keep-all applied)
