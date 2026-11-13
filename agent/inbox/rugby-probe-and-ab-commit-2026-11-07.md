# Rugby: run the CLOB probe now and commit AB (project thread, 18:20Z)

AB has ended (18:05Z). Two pre-authorised steps, no tap needed:
1. Run the outstanding 5-minute CLOB probe now, ahead of window D (8 Nov 13:45Z). Any live market works for a stream test; use the window D tokens (config key D) or any live Polymarket sports tokens, bounded 5 min, one process, nice -n 19, `read_clob` from the merged script, output rugby/probe_clob.jsonl. Report first-message type and rows per minute in the status file. If silent, say so; the REST poll stays the price clock for D and C.
2. Commit the AB raw files and the REST file (AB_clob_rest.jsonl) under reports/rugby-capture/ with a size check first (rugbyrama jsonl is about 500 MB, so commit only the parsed events file rugbyrama_events plus a sha256 and size of the big file, and keep the big one on the volume). Then write agent/outbox/rugby-ab-done-2026-11-07.md.
Note for D and C: the project thread's own 5 s poll showed Top 14 books are very thin (best bid/ask within 10c in 2-7% of polls), so D and C are low priority, but they cost nothing to run on the new script.
