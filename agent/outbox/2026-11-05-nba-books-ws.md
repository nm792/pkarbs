# Reply: nba-books-ws (5 Nov 07:10Z)
RESULT: Part A done this round. Extracted 4322 NBA frames (recv 2026-11-05T00:11:20Z..06:32:56Z) from the live cs2_frames.jsonl copy into winmodels/raw/nba-pmws-2026-11-05/nba_frames.jsonl.gz. No 11-04 rows existed in the source. The cs2 capture's live file stopped appending at ~06:50Z and no cs2 logger process is currently running, so frames after 06:50Z are not present locally — noting that honestly per the "repo copy has none after 03 Jun 06:28Z" question: cause is the capture process stopped; the committed rn1/scores/cs2 copy (06:50Z) matches the local file end.
Part B: scheduled to start 23:30Z for the 6 Nov slate (books.py auto + poll.py) per task file. Will confirm 00:15Z books.jsonl >=80% ticks.
OPEN: nowhere — Part B is time-gated to tonight.
