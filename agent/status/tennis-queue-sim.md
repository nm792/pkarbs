# agent/status/tennis-queue-sim.md
State: STEP 2 (pull) DONE; STEP 3 (queue_sim) BLOCKED — OOM at approved cap.
Last heartbeat: 2026-11-06T00:40Z
Claimed 2026-11-05. Not an approval item (no code change); but step 3 cannot run under the spec's 1.5GB cap and needs an owner ruling.

## Step 1 (git pull): done (on origin/claude/project-thread-vg2ckg tip).
## Step 2 (OddsPapi history pull): DONE. RELAUNCHED 00:05Z, completed 00:19Z.
- Output: /mnt/HC_Volume_107257520/pkarbs/oddspapi/ (154 files in hist/, fixtures_tennis.json.gz 43KB, log.jsonl, bookmakers.json.gz).
- Disk gate GO (pkarbs 500/day, free 26G, cap 20480MB). Time gate met (recorder ended ~21:30Z).
## Step 3 (queue_sim): BLOCKED — kernel OOM under the spec's own cap.
- Command: queue_sim.py <oddspapi> <books> <markets> for the three recorder runs, MemoryMax=1600M (spec: >1.5GB -> stop, never raise).
- Input: merged 3 recorder runs = 1,308,412 book rows / 6,745 market rows (all already tennis tokens, 424 tokens); books gz 257MB.
- Result: unit consumed 1.5G peak -> kernel OOM-killed (systemd 'oom-kill', exit 143). Recurred identically in a second attempt (transient unit + venv python, absolute paths).
- So the intended full-merge input (~1.3M rows) genuinely exceeds ~1.5GB. Per spec step 3 "if it needs more than ~1.5GB RAM, say so and stop" -> stopped, not raising cap unilaterally.
- Box RAM: 7.7GB total, ~4.8GB available; a higher cap is viable but is an owner decision.

## NEEDS OWNER RULING (in-repo question, not a Nick button — no code change)
- Option A: raise MemoryMax for this one bounded run (box has headroom).
- Option B: reduce books input scope (e.g. one recorder run, or a time window) and accept fewer paired matches.
- The prior 7-match run (30edccd7, 09:46Z) used a smaller book set and succeeded; the full-merge is the ">=20 Pinnacle matches" attempt.

## Outputs pending: none committed for step 3 (step 2 raw stays on /vol2 per charter; hourly ship handles it).
