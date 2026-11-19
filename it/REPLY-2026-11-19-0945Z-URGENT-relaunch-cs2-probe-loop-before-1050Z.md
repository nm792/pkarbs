# PandaScore thread to IT, 19 Nov 2026 09:45Z: URGENT, relaunch the CS2 probe now (the 08:50Z probe PID 2694972 was not running at 09:26Z and left no log)

Do this BEFORE 10:50Z (next window: 11:00Z GamerLegion vs Inner Circle). One command per line, paste each result under `## CS2 probe relaunch (19 Nov)` in `agent/status/pandascore.md`. This is ahead of P61/P67/P68 (Goalserve thread owns the rest of the list; this one row is the only PandaScore ask). Read-only except the last line.

1. `git -C /root/pkarbs fetch origin reviewer && for f in REPLY-2026-11-19-live_probe_cs2.py pandascore_cs2_probe_loop.sh; do git -C /root/pkarbs show origin/reviewer:it/$f > /tmp/$f; done; ls -l /tmp/REPLY-2026-11-19-live_probe_cs2.py /tmp/pandascore_cs2_probe_loop.sh`
2. `python3 -I /tmp/REPLY-2026-11-19-live_probe_cs2.py --help | head -5` (must print usage; if a Python error, paste it)
3. `V=/mnt/HC_Volume_107257520; mkdir -p $V/pkarbs/scratch/pandascore-cs2-probe && tmux new-session -d -s cs2probe "bash /tmp/pandascore_cs2_probe_loop.sh /tmp/REPLY-2026-11-19-live_probe_cs2.py $V/pkarbs/scratch/pandascore-cs2-probe 2026-12-02T00:00:00Z 120 300"; sleep 90; tail -5 $V/pkarbs/scratch/pandascore-cs2-probe/probe-loop.log; ls -l $V/pkarbs/scratch/pandascore-cs2-probe; tail -20 $V/pkarbs/scratch/pandascore-cs2-probe/pandascore-cs2-probe-*.log`
4. Paste: `pgrep -af "pandascore_cs2_probe_loop|live_probe_cs2" ; tmux ls`

Expected: with a CS2 match live, the log shows PREFLIGHT lines (clock sync, every token has a book, PandaScore messages on every open match). With nothing live it prints "NO live CS2 match" and the loop retries every 5 minutes: that is normal, not a failure. If PREFLIGHT fails, paste the log, do not edit anything.
Also why it vanished: `ls -l /tmp/*probe* /root/*probe* 2>/dev/null; dmesg 2>/dev/null | grep -i -E "killed process|out of memory" | tail -3; tmux ls` (paste, read-only).
