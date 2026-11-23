# STANDING RULE 2026-11-23 03:05Z: pre-flight on Prime before any recorder or paper start

Nick, 03:01Z 23 Nov: "why are we suddenly getting massive fails on simple tasks like this?"

Why. Every live start in the last 8 hours failed its first health read on something a 60-second check would have caught:
- PK NBA recorder (P106, trading-test d55f38e51): subscribed to 0 tokens and ran two writers on one file.
- PK Goalserve (P101, 1e28fdbbe): the health checker had no mode for this job, so health could not be read.
- Temperature T45 v2 (T57, e92f85c34): 33-51% token coverage ("missing from batch response").
- MFW M49 (f81d494de): sandbox refused cancels and produced invalid maker fills on takes.

Rule, effective now:
1. A project may call a recorder or paper job "ready for IT" only when its commit includes a pre-flight script (preflight.sh or preflight.py) plus the exact command IT runs on Prime BEFORE the start.
2. The pre-flight asserts and prints PASS/FAIL for each item:
   (a) live subscriptions/tokens > 0 AND equal to the expected count (print both numbers);
   (b) a single-instance lock exists (flock or pidfile), and a second copy refuses to start (test it);
   (c) the health checker supports this job's mode (run it once in --test or dry mode);
   (d) at least 60 s of real data from the live feed is written to the output path (print bytes and rows), with prices taken from the token's own book.
3. IT runs the pre-flight first. If any item fails, NOTHING starts: the row goes back to the project as `waiting: preflight FAIL <item>`, with the output committed.
4. The 15-min health read still follows every start (rules 8 and 13).
5. IT does not accept a start row without a pre-flight command. The Reviewer checks this in its 15-min plumbing audit.

Applies to Temperature, MFW, PK arbs, Webb, ASX, Reviewer jobs (the bucket logger, T62) and IT.
