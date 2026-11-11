# Outbox: AB preflight results and start (7 Nov 2026)

From: server-member (Hermes), 13:03Z. Answer to `agent/inbox/rugby-ab-preflight-and-start-2026-11-07.md`.

Preflight re-measured 13:02Z (the 12:30Z/12:48Z heartbeat had relied on the 10:20Z status, so I re-ran each check):
1. Disk: `/` 19G avail of 38G (17G used, 47%). `/mnt/project-files` sits on `/` (findmnt TARGET). Comfortably above the ~2GB AB needs. PASS.
2. ESPN 270559: 200, league = French Top 14. 6 events present, all STATUS_SCHEDULED (604423, 604881, 604418, 604420, 604421, 604422) — matches the 6-match/36-token AB window. PASS.
3. /mnt/project-files/rugby/live-2026-11/ writable. PASS.

Window AB: RUNNING since 13:00:30Z (before the 13:10Z GO). `capture.py --window AB`, timeout 18000, writes rugby/AB_*.jsonl.

ISSUE — duplicate-process race: capture.py has no single-instance lock. AB was launched 5 times (pids 1312662, 1323749, 1335187, 1335303, 1360168, all started 13:00-13:02Z). Five concurrent writers append to the SAME AB_*.jsonl — interleaved rows, duplicated score/price lines; the AB data is not trustworthy until cut to one writer. Fix = kill 4, keep 1. That is a restart/kill => consent-gated; not done in the cron. Please approve consolidation.

The sports/CLOB WS both report open in AB_log.txt.
