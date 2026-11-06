# agent/status/tennis-queue-sim.md
State: STEP 3 RE-RUN DONE (after reviewer fix) — STILL BLOCKED, OOM at approved 1.5 GB cap.
Last heartbeat: 2026-11-06T01:5xZ
Claimed 2026-11-05. Not an approval item (no code change); step 3 cannot complete under the spec's
1.5GB cap even after the reviewer's stream-twice/top-12 fix — needs an owner ruling.

## Step 1 (git pull): done (on origin/claude/project-thread-vg2ckg tip).
## Step 2 (OddsPapi history pull): DONE. 154 hist files / 4.5MB to /vol2.
## Step 3 (queue_sim): STILL BLOCKED — OOM at the cap, after the reviewer's fix.
- Re-run 01:53Z with fixed script 1faba85f (stream twice, top-12 only), MemoryMax=1600M, venv223
  python, all 3 recorder runs + root run: input 1,705,382 book rows / 12,871 market rows.
- Result: kernel OOM-kill (exit 143) again; 1.5G memory peak, 46.4s CPU. The fixed script still
  does not fit the full merge in 1.5 GB. Stopped per the release note ("do not raise the cap").
- Unit qsim-nov5-3.service failed (oom-kill). Launcher /root/pkarbs/run_qsim_nov5.sh.

## NEEDS OWNER RULING (in-repo question)
- Option A: raise MemoryMax for this one bounded run (box ~4.8GB free).
- Option B: reduce books input scope and accept fewer paired matches.
- Reply filed under agent/outbox/tennis-queue-sim-oom-answer-2026-11-06.md.
