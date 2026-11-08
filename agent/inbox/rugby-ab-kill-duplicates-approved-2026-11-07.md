# Inbox: kill 4 of 5 duplicate AB writers (APPROVED, 7 Nov 2026 13:17:45Z)

From: Claude, PK arbs project thread. Nick tapped "Kill 4, keep 1" on the decision card "Kill 4 of the 5 duplicate rugby AB capture processes?" at 13:17:45Z. This is his approval for the kill only.

Do now:
1. Keep the OLDEST AB process (pid 1312662 per your 13:03Z status; confirm with ps start times), kill the other four. Kill only those four pids, nothing else (do not touch other loggers).
2. Confirm in agent/status/rugby-top14-capture.md with `ps` showing exactly one `rugby-top14-capture.py AB` process, and the time of the kill.
3. Do not launch AB again. Stop the dispatch loop from relaunching AB, if it can do that without a code change.
4. Mark in the status which rows in rugby/AB_*.jsonl were written before the kill (interleaved, five writers, 13:00:30Z to kill time), so the lag analysis can dedupe or skip them.

Not approved by this note: any change to rugby-top14-capture.py (for example a single-instance guard). Raise that as a separate request to Nick.
