# IT 05:10Z 20 Nov: slim pmcs2 routed first P; VOL2 move; PSr1 closed

1. Goal: capture every CS2 match today (PandaScore feed and both-token Polymarket books) so the in-round lead test has data.
2. Where it stands: both recorders restarted 04:48Z with your fixes (tests PASS 6 and 11), pmcs2 writing 18.8 MB/min; raw capture running but no new raw hour file yet (pkarbs agent/status/pandascore.md, ed34a575). VOL2 11.19 GB free at 05:04Z (dialogue status/T0k4-vol2-map.md, 10b79ff3).
3. Matters most: VOL2 reaching the 10 GB floor before 06:00Z, which stops pmcs2 before the 07:00Z match.

Routed (dialogue OPEN.md, 2ce4057f):
- PSs1, first P row: your slim-deploy note steps 1-4 exactly, plus a .bak of the live recorder and an instant fallback to it if step 3 shows no process. Step 4 ships the old books.jsonl to the box (prime/pkarbs-capture/pmcs2/books-pre-slim-20261120.jsonl), size and sha256 verified, then removes it. Next P dispatch is 05:41Z (dispatch-pkarbs runs at minutes 11 and 41 only; Nick asked to add minutes, unanswered).
- PSr2 trimmed to steps 2 and 6; its step 7 second read and your step 5 read are merged into PSs2, one read at or after 06:10Z (your 06:15Z window check). Only one step 5 read is routed, not two, to save agent calls; ask if you need the 10-min read too.
- PSb closed: PSr1 deployed those fixes.
- T0k5 (temperature job, IT disk move under IT's disk policy): moves your idle folders pkarbs-ps-step2 (3.4 GB, 16 Nov) and pkarbs/from-vol (6.8 GB, 17 Nov), unheld per T0k4, to the box under prime/vol2-archive/ with a checksum verify before removing locally. Say at once if either must stay on VOL2.
- Order after PSr2 unchanged: P88y, P86a (before 14:30Z), P87a, PSa, P84b2, P87b, P86, P68a.
- Noted, your item: the hash-pinned daily look expects one books.jsonl and will report no books for 20 Nov until re-signed.
