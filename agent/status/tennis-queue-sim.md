# agent/status/tennis-queue-sim.md
State: running (OddsPapi pull RELAUNCHED 2026-11-06T00:05Z after prior 21:35Z run died silently with zero output).
Last heartbeat: 2026-11-06T00:05:35Z
Claimed 2026-11-05. Time-gate met (recorder ended ~21:30Z); not an approval item.
Prior-run incident (filed honestly): status said "running 21:35Z" but no pull_hist process, no oddspapi dir, no committed out_queue_sim_nov5_full.json as of 00:00Z — a false-clear. Relaunched the bounded pull this round.
Run (bounded, memory-capped, single process per protocol):
1. pull_hist.py OUT=/vol2/oddspapi from 2026-11-05T00:00Z to now, --max-fixtures 400 (~165 fixtures, ~15 min, free endpoint). Started 2026-11-06T00:05Z.
2. queue_sim.py next over the recorder runs' books/markets (vol2 pkarbs/tennis 1,048,467 books + /vol tennis-books 129,186 books). Memory-cap ~1.5 GB.
3. Commit ONLY out_queue_sim_nov5_full.json + manifest. Raw stays on /vol2, ships hourly.
Gate: disk_gate pkarbs 500/day -> /vol2/pkarbs/oddspapi = GO (free 26G, cap 20480MB).
Errors: none yet. Outputs pending pull completion (~00:20Z).
