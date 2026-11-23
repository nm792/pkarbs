# P107: restart the Goalserve capture onto the LOCKED build, with the R-058 pre-flight (replaces the restart part of P101)

Why: P101 (02:50Z) ran the committed script without the single-instance lock; R-058 needs lock + pre-flight. Build merged in PR 465 (squash cdc60385cd). Offline tests ALL PASS. A failed pre-flight = nothing counts as started.

SHAs (branch claude/project-thread-vg2ckg for the capture; branch reviewer for the rest):
- live/goalserve/capture_store_all.py = ffe21ca1dd699bb83e5ee170bde5774609d130555148e7c30ded078c20210a84
- live/goalserve/test_capture_store_all.py (21 checks, must end ALL PASS)
- it/goalserve_preflight_r058.py = 20f7efe4e7ab23fd96cca578092646508e68d5358b148376f718f6c245ca928a ; it/test_goalserve_preflight_r058.py (6 checks, ALL PASS)
- it/health_read.py = 5d8646d7fa3137f8ca8a6ca486eeb0494103b79c42f7f22a993c6d239ad29d34 (has the 'capture' mode; your installed copy is a different file)

Steps (Prime). G=/mnt/HC_Volume_107257520/pkarbs/goalserve ; W=/mnt/HC_Volume_107257520/tmp/gs_run
1. FETCH INTO AN EMPTY FOLDER (a new dir, e.g. $W=/mnt/HC_Volume_107257520/tmp/gs_run_$(date -u +%H%M)): never reuse tmp/gs_run, it still holds the OLD writer e61c27ca, which is what failed the first test run. Fetch the 5 files above into $W (git show from the named branches). sha256sum each and compare. Run both tests; each must end ALL PASS. Any mismatch or FAIL: stop, paste, do nothing else.
2. OLD=$(pgrep -f capture); save its script copy as before; kill -INT $OLD (wait for exit). Never run two copies: the key returns 429 if polled twice.
3. cd $W; nohup python3 -I capture_store_all.py >> $G/capture_stdout.log 2>&1 &   (use the same python flags as the old start if it did not use -I)
4. After 60 s: python3 -I $W/goalserve_preflight_r058.py $G $W/capture_store_all.py   (it starts a second copy to prove refusal; exit 3 is the PASS).
5. PASS -> after 15 min: python3 -I $W/health_read.py capture $G --minutes 15 --sports esports,tennis,hockey_nhl . FAIL (either) -> kill the new copy, restart the old script as the fallback, paste both outputs.
Done check: paste the PREFLIGHT VERDICT line and the HEALTH VERDICT line, plus 'pgrep -af capture_store_all' showing one pid.
