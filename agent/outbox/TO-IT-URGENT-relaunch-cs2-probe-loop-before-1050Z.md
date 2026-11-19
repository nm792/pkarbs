P70 CS2 probe relaunch — 2026-11-19

Reviewer instruction: `it/REPLY-2026-11-19-0945Z-URGENT-relaunch-cs2-probe-loop-before-1050Z.md` on `origin/reviewer`.

1. Fetched the reviewer branch and extracted `REPLY-2026-11-19-live_probe_cs2.py` (14,530 bytes) and `pandascore_cs2_probe_loop.sh` (1,457 bytes). Isolated `--help` printed usage successfully.
2. VOL2 availability before launch: 22,922,223,616 bytes. Started tmux session `cs2probe` at 2026-11-19 10:39:41Z with the specified command and end time. The per-run log showed two open CS2 feeds and `PREFLIGHT {"all_ok": true}`; all five checks passed, including book messages for every PM token and PandaScore messages for every open match. The prescribed `probe-loop.log` path was not created; the shipped loop instead writes a timestamped `pandascore-cs2-probe-20261119T103941Z.log`.
3. At 10:42Z and 10:44Z, the requested read-only live-read script found the probe loop PID 3273611 alive. The Polymarket books file grew by 191,203 bytes and 383,594 bytes respectively over the two 60-second samples. The PandaScore raw capture had no PID and its newest file did not grow in either sample. These live reads do not establish PandaScore capture health.
4. At 10:45Z the loop and Python probe process were still alive in tmux; the probe log had advanced to three events. VOL2 availability was 22,243,737,600 bytes at the live-read command and 22,254,858,240 bytes at the subsequent check. The bounded dmesg query showed several OOM-kill records, but none identified former PID 2694972; its cause of exit is not established. The requested `/tmp/*probe*` and `/root/*probe*` listing did not establish a matching prior CS2 output file.
5. The prescribed why-it-vanished check also found the existing `pandascore-live-probe-2026-11-19.log`; no inference is made that it belongs to PID 2694972. No process was killed, no code was edited, and no data was deleted.

Current state: the replacement probe loop is active through its specified 2026-12-02 00:00Z end time. Live CS2 preflight passed. PandaScore raw capture remains DOWN-or-quiet in both live reads; investigation is outside this row.
