# agent/status/tennis-queue-sim.md
State: claimed, gated on the tennis-books-v2 recorder ending.
Last heartbeat: 2026-11-05T18:35Z
Claimed 2026-11-05. The task's own spec runs it AFTER the tennis-books-v2 recorder (tb_capture.py) stops, ~21:30Z. Recorder start 15:10Z, systemd-run timeout 22800s -> ends ~21:30Z. Verified live: python3 /tmp/tb_capture.py ... tennis/2026-11-05 running (pids 554848/554854, cwd /vol2 volume). LoL DK-BLG 22:00Z match has priority per the note.
Not run yet: OddsPapi pull at ~21:30Z (free endpoint, max-fixtures 400, MemoryMax 300M via disk_gate.sh), then queue_sim.py over the three recorder runs' books/markets files, commit only out_queue_sim.json. Gate is a time gate, not a decision item; no Nick approval needed.
Outputs (when run): winmodels/tennis/hist/out_queue_sim_nov5_full.json + manifest; raw stays on /vol2, ships hourly.
Errors: none (not started).
