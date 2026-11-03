# Outbox: stop-shadow-logger approved — STOP GATED ON TERMINAL

**Approvals needed:** the stop itself (approved 507e203 at 14:15Z) — but the stop command cannot run in this cron round; needs an interactive/approved terminal.

**RESULT**
- Offload precondition (step 1) met: data moved + sha-triple-verified raw-2026102619, manifest committed; /dev/sdc 31G free >= 30G.
- Shadow logger confirmed running on pid 2951556 (started 2026-10-25 02:51Z) under pkarbs-shadow-logger.scope, writing to /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/.
- STOP NOT EXECUTED this round: the stop command was refused by the tool consent gate (no user present, cron mode not set to approve). I will not bypass it.

**DATA**
- /proc/2951556/cmdline = /usr/bin/python3 shadow/shadow_logger.py --out /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/
- cgroup 0::/system.slice/pkarbs-shadow-logger.scope

**OPEN / NOT VERIFIED**
- Stop pending: re-issue 'systemctl stop pkarbs-shadow-logger.scope' for pkarbs-shadow-logger.scope in an interactive session, then confirm no shadow_logger.py proc. Do NOT restart.

Count: notes run 5, outstanding 1 (gated stop).
