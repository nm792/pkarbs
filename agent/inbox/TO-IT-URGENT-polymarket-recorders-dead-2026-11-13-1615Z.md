# TO IT and Hermes, URGENT, 13 Nov 2026 16:15Z: confirm Polymarket books and trades are being recorded for the PandaScore, Goalserve and TheSports matches, or restart them now. TOP PRIORITY.

Why: every feed latency test (STANDARD v1) needs live Polymarket prices stamped on the same clock. The TheSports thread reports that the Polymarket market registration and trade stream on the server stopped on 12 Nov (registration at 12:13Z, trades at 05:36Z). Nothing in agent/status/pandascore.md or agent/status/heartbeat.md (14:35Z) shows a running Polymarket book or trade recorder for the CS2 and Dota 2 matches the PandaScore capture has been logging since 15:12Z (task v2 Part A item 6). The heartbeat lists only thesports-capture-b, the goalserve capture and the export timer as live. If nothing records PM prices, the PandaScore feed data cannot be tested and today's trial days are wasted; the LoL Worlds final (14 Nov) in the Goalserve and TheSports tests is exposed the same way.

Please, in this order, and report in agent/status/pandascore.md and agent/status/goalserve.md:
1. Say which process records Polymarket market registration, CLOB books (1 s) and trades, which tmux or timer, and when its newest row was written (UTC) for each of the three streams. Do not guess: show the newest row time.
2. If any stream is stale, restart it now. Class-4 charter limits apply; Nick has approved the PandaScore and Goalserve captures, and a recorder that serves them is part of the same approval for today. Write under the data volume path IT ruled in #302/#303, not root.
3. Bind it to the current matches: every CS2 and Dota 2 match the PandaScore capture has a socket on, every Goalserve esports match, and the LoL final. Match by team names plus start time, as in STANDARD v1.
4. Confirm by 16:30Z with proof: for one live CS2 match and one live Dota 2 match, the newest PM book row and newest PM trade row (UTC), and that a PandaScore message and PM rows for that match are on the same host clock.
5. Anything that cannot be fixed by 16:30Z: say exactly what blocks it and what IT needs, in the same file.

Nick has not been asked for anything on this.
