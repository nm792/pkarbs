# GO from Nick for TASK-tennis-books-2026-11-05 (disk check first)

Nick, 04:43Z 5 Nov, in the project thread: "The disk overflow has been reduced. Check with the agent and then look to run this if it is clear." This is his explicit Go, conditional on the disk check below.

1. Check disk: `df -h /` and the volume used for captures. Record both in agent/status/tennis-books.md.
2. Start ONLY if root `/` is below 75% used AND has at least 10 GB free. If not, do not start: write the numbers in the status file and reply in agent/outbox/2026-11-05-tennis-books.md.
3. If clear, start exactly as in your status "On Go" line (systemd-run scope, MemoryMax=500M, timeout 43500).
4. Size guards while it runs: every hour, after the gzip+commit, delete the local raw files that were committed. Stop the run (kill the scope, keep what is committed) if /root/tennis-books exceeds 2 GB or root free space drops below 5 GB. Note any stop in the status file.
5. Reply in agent/outbox/2026-11-05-tennis-books.md with the df numbers, the start time, the PID/scope, and the first probe rows (clob_rtt, OddsPapi live_odds flag). Never commit the key.
