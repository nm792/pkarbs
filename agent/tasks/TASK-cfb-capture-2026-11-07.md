# TASK: college football (CFB) feed-vs-price capture, Saturday 7 Nov 2026 (optional, bounded)

From: Claude in the PK arbs project thread "Move the $500/day plan forward" (7 Nov 08:55Z). Purpose: the "uncovered sport worth ~$100/day" search. CFB has ~$2.0M/day PM in-play volume (project review 6 Nov), ESPN-fed like NFL. No work has been done on it.

Question (one only): after each CFB score or turnover play on ESPN, how many seconds later does the PM moneyline move 2c, against a random-time placebo?

- Reuse live/nfl_feeds/capture.py (ESPN + books) with the ESPN league path college-football instead of nfl, and the PM CFB markets from gamma (tag college-football), the 3-4 games with the highest PM volume kicking off 7 Nov afternoon/evening US time. One process, bounded 5 h, nice -n 19, MemoryMax 600M, raw data to /vol2 per the server charter.
- Do not start it while rugby window AB (13:15-18:05Z) is running. Start after AB ends (about 18:10Z) and run to about 23:30Z, or skip it if the disk gate (15 GB free twice, 1 h apart) fails.
- Pass: ESPN feed polled with no gap over 30 s and books streaming for 90% of the minutes. No P&L.
- Commit the raw data and write agent/outbox/cfb-capture-done-2026-11-07.md. Analysis happens on the project side.
