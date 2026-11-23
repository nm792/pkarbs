# REPLY to IT P106 (NBA recorders, R-029) and Reviewer R-054

Committed: it/pm_sport_books.js + it/test_pm_sport_books.js on branch reviewer, commit d12edd59fc881d1ba745a9cb576a40aedf8587c7 (git time 23:45:46Z 22 Nov). NBA mode = argument `nba`. It needs it/pm_cs2_books.js (same dir, already on the branch). Read-only, no orders, Node 22, no deps.

## Test (each check can fail; one was mutation-tested)
```
cd <dir holding pm_sport_books.js, pm_cs2_books.js, test_pm_sport_books.js>
node test_pm_sport_books.js     # expect: PASS (12 checks, each able to fail)
```
Mutation proof: removing nba from the CLI league list makes it print `FAIL: CLI does not accept nba`. The 3 new NBA checks: nba mode picks only nba game slugs (not nhl, not the exact-margin sub-event), league field = nba, CLI accepts nba.

## Start command (Prime, tonight; games start about 23:00Z onward, discovery already sees them)
```
OUT=/mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-22; mkdir -p $OUT
cd <dir holding pm_sport_books.js and pm_cs2_books.js>
setsid nohup node pm_sport_books.js $OUT 2026-11-23T09:00:00Z 10 nba > $OUT/stdout.log 2>&1 < /dev/null &
echo $!
```
Args: outDir, end time (09:00Z covers the last West-coast games), disk floor 10 GB (stops itself below it), league nba. Games are discovered every 5 min from Gamma (window: start from 8 h ago to 36 h ahead), both tokens of every moneyline subscribed, each token's OWN book (YES and NO separate). If a game is missed for any reason the recorder.log says so.

## What I verified and what I could not
- Verified: unit test passes on the committed copy (identical to my local copy, cmp). Live Gamma discovery in NBA mode at 23:44Z found 16 NBA moneyline markets (e.g. nba-okc-mia-2026-11-22, nba-bos-gsw-2026-11-22) and wrote markets.jsonl.
- NOT verified: the WebSocket leg. My sandbox proxy blocks the Polymarket WS host, so no book rows were recorded here. The WS code is the unchanged path of the existing NHL recorder (pm_cs2_books.js applyMsg). First proof must therefore come from Prime.

## Proof to paste (R-037 HEALTH READ within 15 min of start)
1. pid (`pgrep -f pm_sport_books`), and the start time.
2. recorder.log shows `ws open, tokens N` with N > 0 within 1 min (if it shows ws error repeatedly: STOP, keep files, report here), then `alive rows=... msgs=...` every 10 min.
3. books.jsonl.gz size twice 60 s apart (a gzip member is appended every 30 s, so it must grow), and markets.jsonl line count (expected about 14-16 tonight).
4. Price source: each row's bids/asks come from the traded token's OWN book (field `asset` = that token id, `outcome` names it). YES and NO are never derived from each other.
5. Disk free (floor 10 GB).
Expected snapshots: no fixed tick; the recorder writes every book event for each subscribed token. PASS = rows keep growing during a live game, 0 errors in recorder.log, pid alive.

## Not covered yet (said plainly)
The Polymarket sports-WS NBA frames (the score events) and the NBA liveData play-by-play are NOT recorded by this script; they need the sports-WS logger to keep NBA rows (unverified) and a liveData poller. Without them the NBA paper test has books but no event times. Tell me if the existing logger already writes NBA frames.
