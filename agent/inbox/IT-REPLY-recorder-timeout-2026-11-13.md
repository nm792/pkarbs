# IT reply, 13 Nov 2026 18:10Z: recorder timeout before the LoL final (#311, #312)

Ruling: Type A (CHARTER clause 22A); #311 and #312 item 2 are merged into dialogue OPEN row P9 (PK arbs, rank 3), deadline moved to 14 Nov 06:00Z.
P9 asks the agent to: drop the `timeout 552000`; run capture.py under Restart=always or a cron watchdog; restart any stream (PM registration, books, trades, pmws, ts_mqtt) whose newest row is older than 10 min, logging each restart; no capture logic change.
Proof in agent/outbox: new unit text, revert copy, newest row UTC per stream.
#312 item 1 (LoL final start UTC, MEASURED from the lolesports hosts, in agent/status/goalserve.md) is part of P9 too.
