# 4 Nov 06:45Z from thread "Recheck NBA at true event time": please run agent/tasks/nba-feed-delay.md tonight

Nick's rule (4 Nov): test each sport at true event time and measure our feed's delay. NBA's own play-by-play has
millisecond event times; we need to know how fast it reaches us live. Please start the capture any time before 23:50Z
(it waits by itself), check it at 00:15Z, copy outputs every 30 min, and write agent/status/nba-feed-delay.md.
Read-only, no orders, one process, 300 MB cap, ends 06:45Z 5 Nov. Also keep the cs2-ws-logger running through 06:45Z
(its NBA frames are the Polymarket side of this test).
