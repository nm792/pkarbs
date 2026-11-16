# TASK (URGENT): add metals, oil and Polymarket commodity perps to the weekend loggers by Thu 20 Nov 2026 12:00Z

Why: forward test of the metals/Brent reopen pattern (weekend-perps/LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md) needs perp price and book depth through the Sunday reopen (about 22:00-23:00Z Sun 23 Nov).
1. Hyperliquid logger: confirm the running `weekend-perps-logger.service` command has `--match` covering GOLD,SILVER,COPPER,PLATINUM,PALLADIUM,BRENT,CL,OIL,NATGAS,EUR,JPY (xyz and flx dexes) in addition to the equity symbols; the logger already stores 5 book levels. If not, update the unit and restart. Keep --interval 60 (use 15 if the load allows from Sun 21:00Z to Mon 00:00Z).
2. Polymarket logger: pull the latest `weekend-perps/pm_weekend_logger.py` (default symbol list now also has GOLD-USD,SILVER-USD,WTIOIL-USD,BRENTOIL-USD) and restart `weekend-perps-pm-logger.service`.
3. Post a short note in agent/outbox with the new commands, plus one row of each new symbol from the first minute of output (row counts and a book sample), by the deadline.
