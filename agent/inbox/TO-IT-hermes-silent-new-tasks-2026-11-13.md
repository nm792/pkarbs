# To IT: agent has been silent since 02:54Z and four new tasks are waiting (13 Nov 05:30Z)

From: Claude, PK arbs project, on Nick's rule (stalled server work is escalated at once, not left overnight).

- Last agent (Prime Bot) commit on origin/claude/project-thread-vg2ckg: 2026-11-13 02:54:03Z (Goalserve capture). Nothing since, 2.5 h. Nick's inbox items #289/#290 (05:01-05:03Z, TheSports export and Goalserve probe) are also unanswered.
- Merged at 05:09Z (PR #273) and waiting for the agent:
  1. agent/TASK-nvda-perp-huang-reaction-2026-11-13.md (read-only history pull, Polymarket NVDA-USD and Hyperliquid xyz:NVDA 1 m candles; NOTE: Claude already pulled the Polymarket/Hyperliquid candles itself, so only the Hyperliquid trades and the headline-time parts remain).
  2. agent/TASK-news-push-latency-test-2026-11-13.md Step 1 (Massive trial key capability check, 30 min; Nick will pass the key to the agent directly, never in Git).
  3. agent/TASK-weekend-perps-logger-2026-11-12.md (Hyperliquid read-only weekend logger; first run is a smoke test).
- Please check: is the agent alive and picking up tasks? Is the 30-minute wake running? Is /vol2 below its floor (status/heartbeat shows VOL2 < 15 GB floor)?
- Rules: read-only market data, no orders, no keys in Git, data on /vol2.
