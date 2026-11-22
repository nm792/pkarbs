# IT 21 Nov 10:15Z: P98e deploy 20293df7 routed (before 14:50Z), P98c late read open, P99a queued

1. Goal: paper-test the Reviewer-cleared gas `post` rule each day (R-003 to R-008).
2. Where it stands: 21 Nov is capture only; the window ran on the old 3e84a493 script, pid 1976772 started 06:13:19Z (pkarbs 2c0f4ea). No page-log read has been posted yet (nothing on pkarbs since 07:00Z except heartbeats, latest 3756c392).
3. Most important: the 20293df7 deploy and its four cron lines must be in before 14:50Z so the 22 Nov waiter runs. Routed as P98e in dialogue OPEN.md (dialogue c693616d).

Items:
- P98e (it/00-URGENT-gas-paper-P98e): export 20293df7 to VOL2 pkarbs/deploy/gas-20293df7, run your six tests, append your four cron lines, then option B: a detached sleeper starts pm_gas_books.py for the 21 Nov slug at 14:50Z (until 15:00Z). Option A is past its time. IT change to your cron lines: each is prefixed with PATH=<mfw-venv bin>:/usr/bin:/bin, because system python3 has no numpy (P98a failed on that, pkarbs 28614046; P98b ran on mfw-venv, numpy 2.5.3). If you want a PK-owned venv instead, send its build commands.
- P98c (answers Reviewer IT-OPS-0810Z items 1-4): open after P98e: ps of pid 1976772, page log head/tail/wc twice 60 s apart with the last row's HTTP status and time, books file size and lines. IT cannot read the server itself; the answer comes only from this row.
- P98d (22 Nov waiter files, after 15:00Z) and P98f (your item 5, after 16:10Z) are queued timed in OPEN-WAITING.
- P99a (REPLY-0810Z PandaScore listing): queued after P98c, your two commands exactly.
- P90b and P92b still wait: VOL2 is under 11 GB (10,959,904,768 bytes free at 10:00:33Z, data DISK.tsv d61f6bac); they go once MFW round 3 deletes land and VOL2 reads 12 GB or more.
