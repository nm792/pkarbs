# Outbox: rugby Top 14 capture nudge (2 Nov 2026)

Task picked up. agent/status/rugby-top14-capture.md is written. CLOB market WS **CONNECTS from the server** (verified this run; the 403 was sandbox-only), so the price clock is the stream, not REST fallback. Harness built (rugby-top14-capture.py, one bounded process per window, MemoryMax 600M, timeout 18000, nice -n 19). Windows AB/C/D scheduled 7-8 Nov, one at a time; AB waits on the 6 Nov gamma confirmation. Nothing running now — windows are future-dated. Status already pushed.
