# Status: cs2-ws-logger — RUNNING, copy refreshed 20:17Z

**State:** RUNNING (transient `cs2-logger.service`, watchdog pid 1533833; node pid re-checked). Last heartbeat 2026-11-04T20:17Z.
**Newest recv:** cs2_frames.jsonl tail `2026-11-04T20:17:32.500Z` — gameId 1789129 INOX vs Johnny Speeds. **Fresh (<1 min), NOT stale → no restart needed.**
**Counts:** 141,630 frames lines (was 106,308 / 30,808 at the 08:05Z note). frames raw 35.1 MB, changes 7.2 MB.
**Hourly copy refreshed this round (20:17Z):** cs2_frames.jsonl.gz (2.3 MB) + cs2_changes.jsonl.gz (0.77 MB) + logger.log.gz → `rn1/scores/cs2/server-2026-11/`, ready to commit.
**Restart check per inbox 2026-11-04-cs2-logger-freshness-0805Z item 3:** newest recv 20:17:32Z, well under the 5-min bound → stay up, no restart (standing approval not needed this round).
**Retention / stop:** logger + watchdog stay up until NBA capture ends 06:45Z 5 Nov, then stop watchdog first, logger second, move /root/cs2logger/out/ to the storage box. Do not restart after 06:45Z.
**Errors:** none. **waiting for Nick:** none.
