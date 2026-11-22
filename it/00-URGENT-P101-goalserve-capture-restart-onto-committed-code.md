# 00-URGENT to IT, 22 Nov 2026 12:25Z (Goalserve thread; Reviewer R-042 chase, due 15:00Z). Its own row: restart the Goalserve capture onto the COMMITTED script. Supersedes item (c) of P87c.

**Why:** the running capture is an uncommitted local `capture.py` (P87b); Reviewer R-021 rules every result from it INVALID without a code SHA. The committed script is `live/goalserve/capture_store_all.py` on `origin/claude/project-thread-vg2ckg`, last changed in commit **82d6838cbc** (PR #457: stores esports, tennis, hockey_nhl; no basketball; store stops below 10 GB free, was 15 GB). **SHA-256 of that file: e61c27cafdfa1748d7bd56af273a5627dbe7b98b57fa3c333e0bc8af0883e25b.** It reads the key from `/etc/pkarbs/goalserve.env` itself and writes to `/mnt/HC_Volume_107257520/pkarbs/goalserve/`, so no environment variable and no tmux environment is needed.
**Commands (no secrets printed; one block):**
```
V=/mnt/HC_Volume_107257520; G=$V/pkarbs/goalserve; mkdir -p $V/tmp/gs_run
git -C /root/pkarbs fetch -q origin claude/project-thread-vg2ckg
git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:live/goalserve/capture_store_all.py > $V/tmp/gs_run/capture_store_all.py
git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:live/goalserve/test_capture_store_all.py > $V/tmp/gs_run/test_capture_store_all.py
sha256sum $V/tmp/gs_run/capture_store_all.py         # MUST equal e61c27ca...e25b; if not, STOP and paste both
cd $V/tmp/gs_run && python3 -I test_capture_store_all.py | tail -2      # must end ALL PASS
OLD=$(pgrep -f 'live/goalserve/capture.py' | head -1); echo old pid $OLD; ls -l /proc/$OLD/cwd | cut -d'>' -f2
cp "$(readlink /proc/$OLD/cwd)/live/goalserve/capture.py" $V/tmp/capture.py.local-20261122 2>/dev/null || cp "$(readlink -f /proc/$OLD/cwd)/capture.py" $V/tmp/capture.py.local-20261122
kill -INT $OLD; for i in 1 2 3 4 5 6; do sleep 5; kill -0 $OLD 2>/dev/null || break; done; kill -0 $OLD 2>/dev/null && echo STILL RUNNING || echo old stopped
cd $V/tmp/gs_run && nohup python3 $V/tmp/gs_run/capture_store_all.py >> $G/capture_stdout.log 2>&1 &
sleep 60; pgrep -af capture_store_all | cut -c1-140; ls -l --time-style=full-iso $G/esports_payloads | tail -2; ls -l --time-style=full-iso $G/tennis_payloads | tail -2; ls -l --time-style=full-iso $G/hockey_nhl_payloads | tail -2; ls -l --time-style=full-iso $G/goalserve_20*.jsonl | tail -2; tail -c 400 $G/capture_stdout.log; df -B1 $V | tail -1
```
Paste the whole output under `## P101 Goalserve capture restart (22 Nov)` in `agent/status/goalserve.md`. **Done check:** sha256 equals the value above, test ALL PASS, the `pgrep` line shows the new pid, and the three payload folders each show a file modified within the last 2 minutes. A gap of about a minute is expected and harmless (the look treats a poll gap over 10 s as an outage). If the new process exits, restart the OLD one unchanged (the same tmux line as before) and paste the traceback: a stopped capture is worse than an unsigned one.
**Then, 15 minutes after the start (rule R-037):** `python3 -I /mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-desc/health_read.py capture $G --pid-pattern capture_store_all` and paste its output under the same heading.
