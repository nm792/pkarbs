# 08:05Z: prove the cs2-ws-logger is still writing (NBA test tonight depends on it)

The newest logger copy in the repo is 03:59Z (commit 8f4e3ce, last frame recv_iso 2026-11-04T03:59:22Z), and the 07:47Z
status repeats the 03:59Z line counts (106,308 / 30,808). Please, this round:
1. Post in agent/status/cs2-ws-logger.md the raw output of
   `wc -l /root/cs2logger/out/cs2_frames.jsonl; tail -c 300 /root/cs2logger/out/cs2_frames.jsonl; tail -3 /root/cs2logger/out/logger.log; ps -o pid,etime,args -p 2758025,1533833`
2. Do the hourly copy now (frames, changes, log gz to rn1/scores/cs2/server-2026-11/) and commit.
3. If the newest recv_iso is more than 5 min old, restart the logger once as now (same unit, same caps). That is
   covered by the standing approval (inbox 2026-11-04-stop-cs2-logger-after-nba item 1), and say so in the status.
