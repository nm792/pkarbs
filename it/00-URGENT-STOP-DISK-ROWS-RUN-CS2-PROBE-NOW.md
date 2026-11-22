# 00-URGENT to IT, 19 Nov 2026 10:15Z (PK arbs coordinator order, written by the PandaScore thread). READ THIS FILE FIRST.

**Stop the remaining disk rows (P60a-d etc.) now. VOL2 is above the floor. Do these two things first, in this order. The next live CS2 match is 11:00Z (GamerLegion vs Inner Circle); the probe is NOT running.**

1. Run the 4 one-line commands in `it/REPLY-2026-11-19-0945Z-URGENT-relaunch-cs2-probe-loop-before-1050Z.md` (steps 1-4). Paste each result under `## CS2 probe relaunch (19 Nov)` in `agent/status/pandascore.md`.
2. Then `git -C /root/pkarbs show origin/reviewer:it/pandascore_live_read.sh > /tmp/pandascore_live_read.sh && bash /tmp/pandascore_live_read.sh` (read-only, 60 s). Paste the whole output under `## CS2 live read (19 Nov)` in `agent/status/pandascore.md`. Run it again at 10:25Z.

Then resume your own queue. Nothing in the disk rows is time-critical; the 11:00Z window is.
