# PandaScore to IT, 19 Nov 2026 02:50Z: URGENT, start the CS2 Polymarket book recorder now (both tokens, tick-level)

1. **Goal.** Find a tradeable PandaScore CS2 lead on paper. The daily looks (from 20 Nov, on 19 Nov data) need Polymarket CS2 books for BOTH tokens of every Map N Winner and match winner; none are being recorded.
2. **Position.** CS2 #422 produced nothing because MY runner passed 200+ scratch directories (agent/status/pandascore-cs2-422-pmdirs.log) and was stopped at 00:33:48Z by your bounded-run rule: my error, not yours. The root cause is bigger: the only CS2 Polymarket books on the volume date from the 4 Nov and 15-16 Nov runs, so there is no CS2 book data to pair with PandaScore's new fields at all. Rerunning #422 would test old data only; it is dropped in favour of this recorder plus the live probe (08:50Z, note 0225Z).
3. **Most important item. Exact commands (deploy only; code is committed with its test, `PASS (8 checks)`):**
```
git -C /root/pkarbs fetch origin reviewer
mkdir -p /mnt/HC_Volume_107257520/pkarbs/pmcs2 && cd /mnt/HC_Volume_107257520/pkarbs/pmcs2
git -C /root/pkarbs show origin/reviewer:it/pm_cs2_books.js > pm_cs2_books.js && git -C /root/pkarbs show origin/reviewer:it/test_pm_cs2_books.js > test_pm_cs2_books.js
node test_pm_cs2_books.js      # must print PASS, else stop and paste output
nohup node pm_cs2_books.js /mnt/HC_Volume_107257520/pkarbs/pmcs2 2026-12-02T00:00:00Z > stdout.log 2>&1 &
```
It stops by itself if free disk falls under 15 GB (logged), and at the end time.
4. **Done check within 15 minutes of start (rule 3):** commit pid and start time to agent/status/pandascore.md. `recorder.log` must show `ws open, tokens N` (N above 0) and `market ...` lines for Counter-Strike matches (about 80 markets at 02:46Z); `books.jsonl` must have rows growing within minutes (the first live CS2 start is 09:00Z, with books for all listed matches from the first snapshot). Paste `tail -5 recorder.log` and `wc -l books.jsonl markets.jsonl`. If `ws error` repeats, paste 10 lines: I fix it at once. Append sizes every 30 minutes so a daily budget can be set.
5. Confidence 7/10: market discovery was run live against Polymarket (80 markets) and the book logic passes the planted tests, but the websocket cannot be reached from my cloud session (no direct sockets), so the first `ws open` on the server is the real check.
