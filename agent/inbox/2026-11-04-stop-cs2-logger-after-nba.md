# 4 Nov 06:50Z from thread "Backtest CS2 on 100+ past matches": stop the cs2-ws-logger after the NBA capture, move its data to the storage box

Nick (4 Nov 06:43Z): "If we do not need the massively resource-hungry logger then tell the agent to move it to the storage box".
That is Nick's go-ahead for this stop. No further approval needed.

Why it is no longer needed: CS2 history now comes from bo3.gg (PRs #47, #49), and LoL, rugby and Dota captures run their own
readers. The one remaining user is the NBA feed-delay task (agent/tasks/nba-feed-delay.md), which needs the logger's NBA frames
until 06:45Z 5 Nov. So:

1. Keep cs2-ws-logger (and its watchdog) running until the NBA capture ends at **06:45Z 5 Nov**. Do not restart it after
   that: if its 12 h timeout ends before then, restart it once as now (same unit, same caps) so the NBA window stays covered.
2. At or after 06:45Z 5 Nov: do a final hourly-style copy (frames, changes, log gz) to rn1/scores/cs2/server-2026-11/ and commit.
3. Stop the watchdog first, then the logger unit (`systemctl stop cs2-logger` or kill the node pid). Confirm both are gone (`ps`, `free -m`).
4. Move /root/cs2logger/out/ (all files) to the storage box at `pkarbs/cs2logger/out/`, using the storage-offload ruling
   (agent/inbox/2026-11-03-storage-offload-ruling.md): rsync --partial, nice/ionice, three-way sha256, manifest lines in
   agent/status/storage-offload-manifest.csv committed and pushed, delete local only after both sha256 match and the
   manifest is pushed. Keep /root/cs2logger/logger.js and watchdog.sh (small) in place.
5. Report in agent/status/cs2-ws-logger.md: State STOPPED, final row counts, GB moved, `df -h /` before and after.
