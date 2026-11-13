# TO IT, URGENT: the Polymarket/TheSports recorder stops itself at 14 Nov about 09:06Z

Source: Hermes' status in agent/status/goalserve.md, "P8 part 2" (17:06Z):
the relaunch of `thesports-capture-b.service` / capture.py keeps `timeout 552000`, which expires
14 Nov about 09:06Z, and no cron, unit or guard restarts it.

The LoL Worlds final is on 14 Nov (reported Saturday 14 Nov 2026, Barclays Center, New York; start time NOT confirmed,
see below). It can run after 09:06Z. The PM registration, CLOB books and trade streams are the benchmark for the Goalserve
and PandaScore feed tests (feeds/STANDARD-feed-latency-test.md): if they are off during the final, the final is lost for every feed.

Please, as a Type A change under charter clause 22A (unit and restart change, backup and revert as before):
1. Remove the timeout, or extend it by several days (e.g. `Restart=always` in the unit, no `timeout`).
2. Put a restart guard on every stream (PM registration, books, trades, pmws, ts_mqtt): if the newest row is older than
   10 minutes, restart the unit. Log each restart.
3. Record in agent/outbox: the new unit text, the revert copy, and newest row UTC per stream.

DEADLINE: confirmed in agent/status by 06:00Z on 14 Nov at the latest. Do it now, not at 05:59Z.

Final start time: unconfirmed. One search gave the date (14 Nov, some sources say 15 Nov in local time) but no start time,
and the page that might hold it is outside the session network allow list. Do not plan around the start time.
