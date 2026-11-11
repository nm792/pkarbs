# QUESTION: tennis-queue-sim step 3 cannot run under spec cap — need owner ruling

Addresses: agent/tasks/TASK-tennis-queue-sim-2026-11-05.md (claimed 2026-11-05)
From: server member. Last heartbeat 2026-11-06T00:40Z.

State: step 1 (pull) and step 2 (OddsPapi history pull, 154 hist files to /vol2) are DONE.
Step 3 (queue_sim) is BLOCKED: the merged full input (1,308,412 book rows / 6,745 market rows
across the three recorder runs, ~174MB books.gz) exceeds the spec's ~1.5GB cap. At MemoryMax=1600M
the kernel OOM-kills queue_sim (systemd oom-kill, exit 143); recurred identically on a second attempt
with absolute paths. Per spec step 3 ("if it needs more than ~1.5GB RAM, say so and stop") I stopped
rather than raise the cap unilaterally. Box has 7.7GB total / ~4.8GB available, so a higher cap is viable.

Ruling requested (no code change either way — pick one):
- Option A: raise MemoryMax for this one bounded run (box has headroom).
- Option B: scope the books input down (one recorder run, or a time window) and accept fewer
  paired Pinnacle matches. Note the prior 7-match run (30edccd7) used a smaller book set and succeeded;
  the full merge is the ">= 20 Pinnacle matches" attempt.

Waiting on owner decision; no Nick button needed (no code change / process kill).
