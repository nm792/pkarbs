# status: nba-books-ws (TASK-nba-books-ws.md)
state: PART A DONE, Part B scheduled for tonight
Part A (5 Nov, this round): extracted NBA frames from full cs2_frames.jsonl (live copy /root/cs2logger/out, captured to 06:50Z) -> winmodels/raw/nba-pmws-2026-11-05/nba_frames.jsonl.gz
rows: 4322 (leagueAbbreviation=nba), recv 2026-11-05T00:11:20Z .. 2026-11-05T06:32:56Z. No 11-04 rows present in source.
Note: cs2 capture process not running as of 09:00Z (cs2_frames.jsonl last write 06:50Z); source has no frames after 06:50Z.
Part B (tonight 6 Nov): start books.py + poll.py by 23:30Z 5 Nov; copy to winmodels/raw/nbacap-2026-11-06 every 30 min; check at 00:15Z. Needs a capture job start (scheduled).
last heartbeat: 2026-11-05T09:0XZ UTC
