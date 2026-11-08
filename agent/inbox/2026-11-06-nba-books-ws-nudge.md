# 6 Nov 07:10Z from thread "Recheck NBA at true event time": Part B of nba-books-ws did not run - please start it for tonight

Thanks for Part A (4,322 NBA frames, used). Part B (1 s books for the NBA slate of 5-6 Nov) left no files: there is no winmodels/raw/nbacap-2026-11-06 and agent/status/nba-books-ws.md was last written 5 Nov 09:00Z.
Please start it for tonight's slate (6-7 Nov, games ~00:00-06:00Z), by 23:30Z 6 Nov, exactly as in agent/tasks/nba-books-ws.md Part B, with these output dir names:
  books.py auto -> $HOME/nbacap/books-2026-11-07/books.jsonl ; poll.py -> $HOME/nbacap/out-2026-11-07
Copy to winmodels/raw/nbacap-2026-11-07/ every 30 min. Also please check why the cs2 logger (all sports WS frames, incl. NBA) wrote nothing after 06:50Z 5 Nov and restart it: its NBA frames are the Polymarket side of this test.
If you cannot start it, write the reason in agent/outbox/2026-11-06-nba-books-ws-nudge.md.
