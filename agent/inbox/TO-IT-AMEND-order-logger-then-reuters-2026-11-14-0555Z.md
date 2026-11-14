# To IT, 14 Nov 05:55Z: AMENDS inbox/TO-IT-URGENT-reuters-retest-late-2026-11-14-0550Z.md (order changed)

New order for pkarbs work, after the Hermes liveness check:
1. Confirm the agent loop is alive (newest Prime Bot commit 04:15Z at 05:50Z).
2. P13 weekend perp logger FIRST. Every hour it waits is weekend data lost for good.
3. Reuters RETEST straight after the logger (task: agent/TASK-rapidapi-reuters-RETEST-2026-11-14.md; short run, about 60-100 calls, no capture). It is NOT to go ahead of the logger, whatever the 05:50Z note said.
4. Verdict file agent/outbox/rapidapi-reuters-RETEST-2026-11-14.md by 07:00Z if that fits; otherwise one line in agent/status with the new time.
