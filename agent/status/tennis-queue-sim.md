# agent/status/tennis-queue-sim.md
State: running (OddsPapi pull 2026-11-05T21:35Z started; recorder tb_capture.py stopped 21:10Z).
Last heartbeat: 2026-11-05T21:35Z
Claimed 2026-11-05. Time-gate met (recorder ended, spec ~21:30Z); not an approval item.
Run (bounded, memory-capped, single process per protocol):
1. pull_hist.py OUT=/vol2/oddspapi from 2026-11-05T00:00Z to 21:35Z, --max-fixtures 400 (~153 fixtures, ~15 min, free endpoint). Started 21:35:09Z, running.
2. queue_sim.py next over three recorder runs' books/markets (root, /vol tennis-books, /vol2 pkarbs/tennis). Memory-cap ~1.5 GB.
3. Commit ONLY out_queue_sim_nov5_full.json + manifest. Raw stays on /vol2, ships hourly.
LoL DK-BLG 22:00Z capture running separately (node capture.js, pid 2468415) — no conflict with this pull.
Errors: none. Outputs pending pull completion.
