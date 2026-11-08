# from_agent reply: rugby AB duplicate writers killed (approved 13:17:45Z, executed 13:33Z)

RESULT
- Killed 6 duplicate AB writers, kept the OLDEST pid 1312662 (start 13:00:30Z). Verified via /proc: only 1312662 alive; 1323749/1335187/1335303/1360168/1487818/1632185 gone.
- Note expected 5 writers; the dispatch loop had relaunched 2 more by execution time (7 live). All 6 duplicates killed under the 13:17:45Z approval; status agent/status/rugby-top14-capture.md records kill time + interleaving window.
- AB jsonl interleaving window 13:00:30Z..13:33Z is marked for dedupe/skip in the lag analysis.
- No code change applied (no single-instance guard); that remains a separate Nick request per the note.

OPEN / NOT VERIFIED
- Dispatch loop can still relaunch AB (no code change made); AB stays single-writer only until a guard or loop change is approved.
Count: notes run 1, outstanding 0.
