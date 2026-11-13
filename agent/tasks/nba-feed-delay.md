# TASK: live NBA feed-delay capture, night of 4-5 Nov 2026 (OPEN, run tonight)

Owner thread: "Recheck NBA at true event time" (branch claude/project-thread-zzexus). Written 4 Nov 06:45Z.

## Question (one only)
For the 14 NBA games starting 5 Nov 00:00Z-03:30Z, how many seconds after the true event time (NBA official `timeActual`)
does each score change reach us from (a) the NBA's own liveData play-by-play (S3 origin of cdn.nba.com) and (b) ESPN's summary API?
The Polymarket sports WS side is already captured by the running cs2-ws-logger (it carries NBA frames) - nothing to add there.

## Pass / fail, fixed before running
- PASS (capture): at least 8 of the 14 games have nba_actions.jsonl rows covering at least 80% of their score changes, and
  at least 90% of polls return 200 or 304 (no 403/429 storms).
- FAIL: fewer than 8 games. Report which games failed and the HTTP codes in polls.jsonl. No delay figures then.
- Read-only. No orders, no P&L.

## Run (bounded, one process, stdlib python3 only)
```
cd agent/tasks/nba-feed-delay
OUT=$HOME/nbacap/out-2026-11-05; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 27000 \
  python3 poll.py $OUT 2026-11-04T23:50:00Z 2026-11-05T06:45:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
- It sleeps until 23:50Z by itself, starts one thread per live game, and exits at 06:45Z (or when the timeout hits).
- Load: NBA S3 play-by-play 1 req/s per live game (ETag conditional, mostly 304s), ESPN summary 1 req per 2 s per live game,
  two scoreboards every 15 s. Peak ~10 live games -> ~15 req/s total, under 1 MB/s.
- First check (00:15Z): `tail $OUT/log.jsonl; wc -l $OUT/*.jsonl`. If polls.jsonl shows repeated 403/429, kill the process and report.
- Copy $OUT/* to the repo at winmodels/raw/nbacap-2026-11-05/ (gzip) every 30 min and at the end, from scratch (never append into the repo).
- Clean up at the end: confirm the python process is gone (`ps`, `free -m`) and say so in agent/status/nba-feed-delay.md.

## Local test (done 4 Nov 06:40Z in the Claude sandbox)
- Against finished game 0022600171 (LAC-TOR) and ESPN 401909920: 638 NBA actions and 546 ESPN plays written; both hosts return 200.

## Report to agent/status/nba-feed-delay.md
Row counts per file, games started (log.jsonl), HTTP code counts from polls.jsonl, process cleanup. The owner thread does the analysis.
