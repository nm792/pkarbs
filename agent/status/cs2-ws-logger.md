# Status: cs2-ws-logger

State: RUNNING. Last heartbeat 2026-11-04T07:47Z.
- logger node pid 2758025 (from /proc), watchdog pid 1533833. cs2-logger.service transient unit shows prior 12 h timeout end; watchdog keeps the process alive.
- Output /root/cs2logger/out/: cs2_frames.jsonl 106,308+ lines (accumulates), cs2_changes.jsonl 30,808+.
- MUST be kept running through 06:45Z 5 Nov (NBA feed-delay needs its frames). If its 12 h timeout lapses before then, restart once as-now.
- AFTER 06:45Z 5 Nov (inbox 2026-11-04-stop-cs2-logger-after-nba): final hourly-style copy to rn1/scores/cs2/server-2026-11/, stop watchdog then logger (confirm both gone via ps/free), move /root/cs2logger/out to storage box pkarbs/cs2logger/out/ per storage-offload ruling (rsync --partial, sha256, manifest), keep logger.js+watchdog.sh. Report STOPPED with rows/GB/df-before-after.
