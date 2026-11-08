# TASK (Hermes): rugby windows D and C preflight, answer by 12:45Z 8 Nov (read-only checks, no restarts)

From: Claude, PK arbs rugby thread (via coordinator, for Nick). Window D starts 13:45Z, C at 19:50Z.

Report in agent/outbox/rugby-d-c-preflight-2026-11-08.md, each as YES/NO with the command output:
1. Is window D scheduled to launch at 13:45Z (what launches it: cron, at, systemd timer, or you)? Show the entry. Same for C at 19:50Z.
2. Does the launched capture.py include the single-instance flock guard (#187, ce3166ab)? Show `grep -n flock` on the file that will run.
3. Where will D write? The script has ROOT=/root/pkarbs/rugby. Is that on the root disk or on /vol2 (show `df -h /root/pkarbs/rugby /vol2` and `readlink -f /root/pkarbs/rugby`)? The 5 Nov server charter says no PK arbs raw data on the root disk. AB left a 1.32 GB Rugbyrama file; show its location and free space on root and /vol2.
4. The 18:33Z probe still showed 0 CLOB messages on the new code. State the D plan for prices: REST 5 s fallback (which tokens), and say plainly that the stream is not fixed.

Do not change code or paths on your own. If 3 is the root disk, say so and wait: moving ROOT to /vol2 is a code change that needs Nick's approval (requested in the thread).
