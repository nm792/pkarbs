# Rugby: 5-minute live summary during matches (Nick, 7 Nov 09:14Z, via project thread)

Nick asked for a quick data summary every 5 minutes during each match, so the thread can watch the capture live.

Done in the harness, nothing for you to build: agent/tasks/rugby-top14-capture.py now runs a fifth async task, `summarise`. Every 300 s it appends one block to rugby/<win>_summary.md and writes the same block straight to /mnt/project-files/rugby/live-2026-11/<win>_summary.md (no need to wait for the 10-minute copy or a commit). Each block lists, for matches between kickoff minus 20 min and kickoff plus 135 min: stream message counts, best bid/ask, trade count and last trade price per outcome, sports WS rutopft message total, ESPN poll ok/error counts and latest score, latest Rugbyrama event. Counts only, no P&L.

Please:
1. Pull origin/claude/project-thread-vg2ckg before the 12:30Z preflight (also contains the user-agent change, see user-agent-no-email-2026-11-07.md).
2. At preflight confirm the file path /mnt/project-files/rugby/live-2026-11/ is writable from the server.
3. In the first 15 minutes of the run, check that AB_summary.md has a block every 5 minutes and write one line in agent/status/rugby-top14-capture.md. If a block is missing or the task errors, the log shows "summary error"; fix and tell the thread, but do not restart the capture unless the summary task cannot be repaired otherwise.
