# 00-URGENT to IT, 21 Nov 2026 23:58Z (Goalserve thread; Nick 23:50Z: "where are the esports and other sports results?"). Answers P87b (your 20 Nov 21:42Z note) and asks for 4 read-only pastes. Sorry for the 26 h delay on my side.

**Why now:** VOL2 has been 9-11 GB free since 20 Nov, and the Goalserve capture store AND the daily look both stop at 15 GB. So the 20 Nov and 21 Nov looks very likely did not run and the store may have paused (UNVERIFIED: I have not seen LATEST-esports.tail or a hour-file listing). PR #457 (squash 82d6838c) lowers the store floor to 10 GB (IT's floor) and the look gate to 10.5 GB. It only takes effect after the capture restart below.

**Answers to P87b (a)-(d):**
(a) Run `live/goalserve/capture_store_all.py` from origin/claude/project-thread-vg2ckg (commit 82d6838c or later): it stores esports, tennis and hockey_nhl, no basketball, 10 GB floor.
(b) The uncommitted local `capture.py` is the earlier store-all version; keep a copy, do not discard: `cp <local capture.py> /mnt/HC_Volume_107257520/tmp/capture.py.local-20261121` and paste `diff` of it against `git show origin/claude/project-thread-vg2ckg:live/goalserve/capture_store_all.py` (cut -c1-200, first 40 lines).
(c) Restart (no secrets printed): `PID=$(pgrep -f 'live/goalserve/capture.py' | head -1); readlink /proc/$PID/cwd; tr '\0' ' ' < /proc/$PID/cmdline` (paste those two lines), `git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:live/goalserve/capture_store_all.py > /mnt/HC_Volume_107257520/tmp/capture_store_all.py` (do not write into the git tree), then in the SAME tmux window and environment that the current capture was started in: stop the old process (`kill -INT $PID`, wait for it to exit), then start the same command line with `capture_store_all.py` from the new path. Paste `pgrep -af capture_store_all`.
(d) No quiet gap is needed: a restart is a gap of seconds, the daily look treats any poll gap over 10 s as an outage and clears baselines. Do it at once, before any other Goalserve step.

**Reads (paste under `## P87c (21 Nov)` in `agent/status/goalserve.md`):**
1. `G=/mnt/HC_Volume_107257520/pkarbs/goalserve; for s in esports tennis hockey_nhl basketball; do echo $s; ls -l --time-style=full-iso $G/${s}_payloads/ | tail -3; ls $G/${s}_payloads/*STOP* $G/${s}_payloads_STOP.log 2>/dev/null; done; cat $G/*STOP.log 2>/dev/null | tail -6; df -B1 /mnt/HC_Volume_107257520 | tail -1`
2. `L=/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-daily-logs; ls -l --time-style=full-iso $L | tail -8; tail -c 1500 $L/LATEST-esports.tail; tail -c 1500 $L/LATEST-tennis.tail`
3. `du -sh /mnt/HC_Volume_107257520/pkarbs/goalserve/*_payloads | sort -h | tail -6`
4. After the restart, if VOL2 free is 10.5 GB or more: `V=/mnt/HC_Volume_107257520; cd /root/pkarbs; MIN_FREE=10500000000 ENVFILE=/root/ship/ship.env bash /root/ship/daily_look_cron.sh` and paste the last 25 lines of `$L/look-esports-*.log` (newest). If it STOPs on missing hour files, paste the exact STOP line and do nothing more: that needs a pre-registration amendment, which I will write.
**Basketball:** after the restart, `basketball_payloads` is dead weight (NBA is dropped by Nick). Paste its `du -sh` (read 3) and, once pasted, delete it: this note is the written confirmation I promised in P87.
**Done check:** reads 1-3 and the restart `pgrep` line pasted; read 4 if disk allows.
