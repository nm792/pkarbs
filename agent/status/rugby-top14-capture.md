# Status: rugby Top 14 capture (task TASK-rugby-top14-capture-2026-11-07)

state: AB WINDOW RUNNING since 2026-11-07T13:00:30Z; single writer confirmed 13:33Z
last agent write: 2026-11-07 13:33 UTC (kill of duplicate AB writers per Nick's 13:17:45Z approval)

## DUPLICATE AB WRITER KILL — DONE (approved 13:17:45Z, executed 13:33Z)
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

## Windows
- AB: RUNNING 13:00:30Z..~18:00Z (bounded 18000s). Matches kick 13:30Z (2) + 15:35Z (4).
- D: 8 Nov 13:45-16:30 UTC. C: 8 Nov 19:50-22:35 UTC. Each starts after prior reviewed.

## Outputs
- Scratch: rugby/AB_*.jsonl (espn ~11MB, rugbyrama ~379MB, events ~152KB at 13:32Z).
- 5-min summaries committed to reports/rugby-capture/AB_summary.md + AB_log_tail.txt per note.
- Final commit under reports/rugby-capture/ at window end.
