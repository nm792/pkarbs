# agent/status/tennis-queue-sim.md
State: STEP 3 RE-RUN DONE — PASS (reviewer float64 fix, no OOM). Result committed.
Last heartbeat: 2026-11-06T02:2xZ
Claimed 2026-11-05. Not an approval item (no code change).

## Step 3 (queue_sim) — DONE 02:18Z
- Reviewer answer2 (float64 flat-snapshot fix, default-branch 3b579369) pulled; queue_sim.py has NL=12 / flat float64 (~200 B/row).
- Re-run 02:18Z, same 1.5 GB cap (MemoryMax=1600M, MemorySwapMax=0), venv223, all 3 recorder runs.
- Result: NO OOM. Paired Pinnacle **53**, bet365 **54** matches. PASS line met (>=20 Pinnacle).
  - pinnacle ack0.2 per_match -0.15..+0.06 (ci90 crosses 0); bet365 ack0.2 per_match 6.65 (ci90 [-12.89,28.48]).
- out committed: winmodels/tennis/hist/out_queue_sim_nov5_full.json (1,763 B).
Criteria: >=20 paired Pinnacle => verdict; reached (53). Earlier runs had only 7.
