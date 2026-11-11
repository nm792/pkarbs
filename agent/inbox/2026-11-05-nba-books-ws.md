# 5 Nov 07:10Z from thread "Recheck NBA at true event time": please run agent/tasks/nba-books-ws.md

Thanks for the 4-5 Nov nba-feed-delay capture (it ran the whole night; useful). Two things for the next NBA slate:
(A) one-off: extract the NBA frames from the full cs2_frames file for 5 Nov (the repo copy has none after 3 Nov 06:28Z), (B) tonight 6 Nov 00:00-06:30Z: 1 s order-book capture (books.py auto) plus poll.py. Read-only, bounded, details in the task file.
