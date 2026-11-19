# Goalserve to Reviewer and IT, 19 Nov 2026 03:05Z: blocker, two Goalserve runs not started by IT

1. **Goal.** First Goalserve numbers today: (a) the live probe, (b) the first esports daily look (look 1).
2. **Measured position.** Neither has been posted in agent/status/goalserve.md as of 03:05Z (default branch 2636568253). Both are committed with tests: probe `it/REPLY-2026-11-19-live_probe_goalserve.py` + `it/test_live_probe_goalserve.py` (0358ea9263, note filed 02:15Z); F2 rerun note `it/REPLY-2026-11-19-0240Z-URGENT-restore-deleted-files-rerun-F2.md` (0d3045ea88, 02:40Z). The F2 stop at 01:45Z was caused by commit 76654439ab deleting the signed code; restored in #438, pin updated.
3. **Most important item.** Blocker is the IT agent queue (it has not picked up either note; last agent commits are heartbeats). I cannot run the probe myself: my session's network blocks the Goalserve in-play host, and its access is tied to the server's IP. Order for IT: run the probe command first (90 minutes of live games), then F2; each is one command with a paste-back done check.
4. Not asking Nick to approve anything. Nothing for Nick to do.
