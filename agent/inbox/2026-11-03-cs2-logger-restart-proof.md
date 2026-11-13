# Inbox: prove the CS2 WS logger restarted after its 12 h limit

From: project thread (PK arbs), 3 Nov 2026 02:40Z
To: server agent (Hermes)

The cs2-logger run started 2 Nov 14:10:02Z with `timeout 43200`, so it hit its limit at ~02:10Z on 3 Nov.
Your heartbeats say RUNNING, but nothing outside the server shows it: no CS2 frames from the server
have ever been copied to the repo or the shared folder.

Please, this round:
1. If the logger is NOT running, restart it with the same config (keep-all, MemoryMax=512M,
   MemorySwapMax=0, timeout 43200, single process). This restart is already approved by Nick
   (2 Nov 14:35Z, agent/inbox/2026-11-02-cricket-capture-approved.md). Do not change anything else.
2. In agent/status/cs2-ws-logger.md, record: current PID, ExecMainStartTimestamp, the gap (if any)
   between the old run ending and the new one starting, and the line count of cs2_frames.jsonl
   with receive time after 2026-11-03T02:10Z.
3. Commit a copy of the raw output (cs2_frames.jsonl, cs2_changes.jsonl, logger.log, gzipped if large)
   to rn1/scores/cs2/server-2026-11/ in this repo, and keep doing that every hour while it runs
   (task step 2). This is a read-only copy, no code change or restart needed.

Reply in agent/outbox/2026-11-03-cs2-logger-restart-proof.md.
