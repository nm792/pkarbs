# TASK: NBA 1 s order books + Polymarket WS frames, night of 5-6 Nov 2026 (OPEN)

Owner thread: "Recheck NBA at true event time" (branch claude/project-thread-zzexus). Written 5 Nov 07:10Z. Follows agent/tasks/nba-feed-delay.md (same night pattern).

## Why
Nick's rules: quote each feed's delay against the Polymarket PRICE, and test queue position. We have only 5 minutes of 1 s books and
32 Polymarket-WS score matches from 5 Nov (the sandbox was cut off at 02:57Z). Tonight's slate needs a full-night capture on the server.

## Part A (do now, one-off): extract NBA frames already logged
The cs2-ws-logger keeps ALL sports-WS messages. From its full `cs2_frames.jsonl` copy every frame with `"leagueAbbreviation":"nba"` and
recv time 2026-11-05T00:00Z-07:00Z (and 2026-11-04 if present) to `winmodels/raw/nba-pmws-2026-11-05/nba_frames.jsonl.gz` in the repo. Report the row count and
the first/last recv_iso in agent/status/nba-books-ws.md. (The repo copy of cs2_frames.jsonl.gz has no NBA rows after 3 Nov 06:28Z: check why - rotated file? filter in the copy script?)

## Part B (tonight): 1 s CLOB books for every NBA moneyline
```
cd agent/tasks/nba-feed-delay
OUT=$HOME/nbacap/books-2026-11-06; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 30000 \
  python3 books.py auto $OUT/books.jsonl 29000 > $OUT/stdout.log 2>&1 < /dev/null &
```
- Start by 23:30Z 5 Nov (it discovers games itself every 10 min from the NBA liveData scoreboard + Polymarket slugs; stdlib only).
- Also run the existing poll.py for 6 Nov: `python3 poll.py $HOME/nbacap/out-2026-11-06 2026-11-05T23:50:00Z 2026-11-06T06:45:00Z`.
- Load: one batched POST /books per second (all NBA tokens, ~28) + poll.py's ~15 req/s. Pass: books.jsonl has >= 80% of 1 s ticks per live game window. Check at 00:15Z.
- Copy `books.jsonl`, `books.jsonl.markets.json` (gzip) to `winmodels/raw/nbacap-2026-11-06/` every 30 min and at the end, from scratch.
- Clean up at the end and say so in the status file.

Read-only. No orders.
