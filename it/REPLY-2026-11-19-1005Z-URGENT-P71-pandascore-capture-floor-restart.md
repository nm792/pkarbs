# PandaScore thread to IT, 19 Nov 2026 11:05Z: P71 (PandaScore RAW capture not writing since 16 Nov). Likely cause found, exact commands below.

**Likely cause:** `live/pandascore/ll_capture.py` line 31 is `FLOOR = 15e9` and lines 104-106 do `if not free_ok(): ... sys.exit(0)`. VOL2 fell below 15 GB, so it stopped itself, exactly like the CS2 book recorder at 05:21Z. Not yet confirmed from its log (step 1 confirms). Fix: a byte-identical copy of the approved file (sha256 be437551ef87...) where only that one line reads the floor from `PS_FLOOR_GB` (default 15, so nothing else changes). Test below fails on any other diff. Do NOT edit `live/pandascore/ll_capture.py` itself.

One command per line. Paste results under `## PandaScore capture restart (P71, 19 Nov)` in `agent/status/pandascore.md`.

1. (read-only, confirms the cause) `tmux ls; tmux capture-pane -p -t pandascore -S -40 2>&1 | tail -15; pgrep -af ll_capture; ls -l --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | tail -3`
2. (fetch + test) `git -C /root/pkarbs fetch -q origin reviewer claude/project-thread-vg2ckg; for f in ll_capture_floor_env.py test_ll_capture_floor_env.py; do git -C /root/pkarbs show origin/reviewer:it/$f > /tmp/$f; done; git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:live/pandascore/ll_capture.py > /tmp/ll_orig.py; sha256sum /tmp/ll_orig.py; python3 /tmp/test_ll_capture_floor_env.py /tmp/ll_orig.py /tmp/ll_capture_floor_env.py`  (expect sha256 starting `be437551ef87` and `PASS (4 checks, each able to fail)`; if either differs, stop and paste)
3. (start, only if step 1 `pgrep` printed nothing) `tmux new-session -d -s pscap2 "PS_FLOOR_GB=10 python3 -u /tmp/ll_capture_floor_env.py >> /tmp/pscap2.log 2>&1"; sleep 90; pgrep -af ll_capture_floor_env; tail -5 /tmp/pscap2.log; ls -l --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | tail -2`
4. (growth, 60 s apart, proves it is writing) `f=$(ls -t /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/*.gz | head -1); stat -c %s $f; sleep 60; stat -c %s $f`

Expected: log shows sockets connecting per open CS2/Dota match; file size rises between the two `stat` lines. If no match is live the file may grow only slowly; paste it anyway. Disk: VOL2 21-22 GB free, the floor is 10 GB; IT's own 25 GB ship target stands.
