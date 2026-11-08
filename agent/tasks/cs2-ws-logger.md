# TASK: CS2 live score logger (Polymarket sports WS), server run

**Question this task answers:** does the Polymarket sports WebSocket emit a CS2 score-string change for each round, and how many change records per live match-hour do we capture with receive timestamps?

**Pass/fail, fixed before the run:**
- PASS if the log holds at least one change record per live CS2 match in which the score's first field (rounds in the current map) moves by 1 at a time, and no gap longer than 90 s between frames while a match is running.
- FAIL otherwise. On FAIL, report the examples and do not run the markout.

**Scope and limits (PROTOCOL.md rules 1-6):**
- Single process. Runtime cap 12 h: `timeout 43200`.
- Memory cap: `systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0 timeout 43200 node logger.js`.
- Output is streamed to JSONL, not held in memory. Nothing is loaded whole.
- Needs `ws` (npm i ws@8) and outbound access to sports-api.polymarket.com.
- Watchdog (`watchdog.sh`) restarts the logger if it is not running or its last frame is over 90 s old. Run one watchdog only.

**Run:**
1. `npm i ws@8` in a scratch directory, then `OUT=<scratch>/out HOURS=12 node logger.js` under the systemd-run wrapper above.
2. Copy the output to the repo or project folder every 10 min, from scratch, never by appending to a shared folder.

**Clean up when done (rule 4):** stop the logger and watchdog, delete temp files, and report `ps` and `free -m`.

**Notes:**
- The Polymarket docs don't define the score string. Our reading is "rounds in current map | map wins | format"; verify it against the first captured match before using it.
- Receive time is the only clock. Round timing precision is therefore approximate.
