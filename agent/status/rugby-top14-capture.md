# rugby-top14-capture status

Nick approved "kill 4 keep 1" at 13:17:45Z. At execution time 7 AB pythons were live
(the dispatch loop had relaunched 2 more after the note); kept the OLDEST (1312662,
start 13:00:30Z) and killed the other 6 (1323749, 1335187, 1335303, 1360168, 1487818,
1632185). Verified: only 1312662 remains alive; the 6 killed pids are gone from /proc.

AB jsonl interleaving window: 5 writers wrote 13:00:30Z..~13:17Z, 7 writers to kill time
13:33Z. Rows in rugby/AB_{espn,rugbyrama,rugbyrama_events}.jsonl within that span may
be interleaved/duplicated from concurrent append writers; the lag analysis should
dedupe or skip rows attributed to 13:00:30Z..13:33Z. Single-writer rows continue after
13:33Z. No code change made (single-instance guard NOT added — that stays a separate
Nick request per the note).

## CLOB live check (13:50Z reviewer note; answered 14:37Z)
- Case 4: CLOB WS stream writes zero rows — AB_clob.jsonl / AB_trades / AB_sports
  do not exist; AB_log.txt shows "CLOB open" then silence (no close/error). Socket
  connected (1312662, 2 ESTAB) but no market-channel rows land in the WS file.
- **REST fallback already live**: rugby-clob-rest-fallback.py pid 1806719 (started
  ~13:55Z) writes AB_clob_rest.jsonl (1.25 MB, mode "5s-poll", streamed thru 14:36Z).
  Covers live match tokens per the pre-approved 5s book poll.
- Summariser reads the WS filename (absent) hence "CLOB 0" — read-path mismatch, not
  missing data. Wiring summariser to AB_clob_rest is a script change (gated).
- No restart performed (not authorised). Reply in agent/outbox.

## Windows
- AB: RUNNING 13:00:30Z..~18:00Z (bounded 18000s). Matches kick 13:30Z (2) + 15:35Z (4).
- D: 8 Nov 13:45-16:30 UTC. C: 8 Nov 19:50-22:35 UTC. Each starts after prior reviewed.

## Outputs
- Scratch: rugby/AB_*.jsonl (espn ~14MB, rugbyrama ~510MB, events ~168KB, clob_rest ~1.25MB at ~14:36Z).
- 5-min summaries committed to reports/rugby-capture/AB_summary.md + AB_log_tail.txt per note.
- Final commit under reports/rugby-capture/ at window end.
