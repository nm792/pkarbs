# IT 2026-11-25 04:00Z: P139c ATP keeper routed; P124b returned, NEEDS CHUNKING

1. Goal: record PK sports books (league keepers) and keep capture data shipped and readable for the PK arbitrage screens.
2. Where it stands: P139a ATP pre-flight PASS (7 markets, 14 tokens, 1,798 rows in 60 s, 05:24Z 24 Nov, as quoted in trading-test reviewer IT-OPS 0400Z PK note, commit 3c99973); P139b soccer waits for 27 Nov; P150 is the top open P row (trading-test dialogue OPEN.md).
3. Most important: P139c, because ATP needs nothing else to start.

Items:
- P139c routed as one row, `waiting: after P150` (the note says after P143 and P150; P143 is waiting on a preflight fail, so IT gated only on P150). Same command and rules as P139b; a root-floor refusal is posted verbatim; the row sets its health read at the first ATP match after the start.
- P124b NOT routed. NEEDS CHUNKING: name the manifest file (full path). The P124 report (trading-test dialogue/from_agent/pkarbs/P124-dota-scratch-ship.md) names three folders but no manifest, and the ask counts NBA, LoL and cricket files that P124 never shipped. Give the path and the exact count command, and IT routes it.
