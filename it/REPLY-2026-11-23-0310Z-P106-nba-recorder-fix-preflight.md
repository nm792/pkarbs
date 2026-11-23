# REPLY R-057 (1), R-058 (P106 NBA recorder) - fixed code f5be71e7f34953fadca6147187c7a79b71081a37 (reviewer branch, git time 03:07:26Z 23 Nov)

## Cause of 'ws open, tokens 0'
pm_sport_books.js started its websocket loop and its Gamma discovery at the same time. The socket connected before the first discovery had filled the token list, so it logged 'ws open, tokens 0' and sent an EMPTY subscription; markets were meant to arrive later through a 'subscribe' message that I never proved works. My 22 Nov test could not catch it because it only tested market picking (my sandbox cannot reach the Polymarket websocket). Reproduced now: with the new wait removed, the local live-path test prints exactly 'ws open, tokens 0', 0 rows, PREFLIGHT FAIL. The 01:13-now capture is UNVERIFIED (rows may be missing for every game since start).
The two writers: the keep-alive matched the recorder with an absolute-path pgrep, but the process shows as 'node pm_sport_books.js', so it never matched and started a second copy. The old recorder had no lock.

## What is fixed (all in it/, each test can fail; I mutation-tested the first two)
(a) The recorder never opens the socket with 0 tokens (waits for discovery). If no NBA token exists 120 s after start it logs FATAL and exits 4 (ALLOW_IDLE=1 only for a no-game window). Test: test_pm_sport_books_live.js (8 checks, local fake Gamma + fake websocket): ws open says tokens 2, 0 markets => preflight exit 5 and normal run exit 4.
(b) Single instance: pidfile OUT/recorder.pid (O_EXCL; live pid => the second copy exits 2 'REFUSED'; stale pid is taken over). Keep-alive nba_keepalive.sh matches by pidfile + /proc cmdline, never by pgrep. Test: test_nba_keepalive.sh (4 checks: running recorder NOT relaunched; dead, stale and unrelated pid ARE relaunched).
(c) Pre-flight mode (R-058): `node pm_sport_books.js <dir> '' 10 nba preflight 60` runs 60 s on real Gamma + websocket and exits 0 ONLY if ws tokens = 2 x markets found, tokens > 0 and rows were written; else exit 5 and prints the JSON verdict.
Tests to run on Prime from the committed copy (all must print PASS): `node test_pm_sport_books.js` (12), `node test_pm_sport_books_live.js` (8), `bash test_nba_keepalive.sh` (4).

## IT steps (nothing starts unless every pre-flight line passes)
1. Stop BOTH old recorder pids (3989182 and 3990021): the old code has no lock, so a mixed state would write twice. Keep every file; no deletes; move nothing.
2. Fetch f5be71e7 copies of it/pm_sport_books.js, it/pm_cs2_books.js, it/nba_keepalive.sh and the three tests into one directory; run the three tests: all PASS.
3. Pre-flight on Prime, separate dir: `cd <dir>; node pm_sport_books.js /mnt/HC_Volume_107257520/pkarbs/pmnba/preflight-$(date -u +%H%M) '' 10 nba preflight 60; echo exit=$?` Required: exit=0, JSON preflight PASS, ws_tokens = expected_tokens > 0, rows_written > 0.
4. Single-instance proof: start the real run (below), then immediately run the same command again: it must print REFUSED and exit 2.
5. Real start: `OUT=/mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-23; bash nba_keepalive.sh $OUT 2026-11-24T09:00:00Z 10 nba` (cron once a minute is safe: a running recorder is not relaunched). Do NOT reuse the old OUT dir for the new run if its recorder.log is needed as evidence; the pidfile is the only state.
6. R-037 HEALTH READ within 15 min: pid (from recorder.pid and `pgrep -af pm_sport_books` showing ONE), recorder.log lines 'ws open, tokens N' (N > 0, N = 2 x markets) and 'alive rows=... ws_tokens=N', books.jsonl.gz size twice 60 s apart (appends every 30 s), markets.jsonl line count, disk free. Any fail: stop, keep files, report.
Expected snapshots: no fixed tick; every book event of each subscribed own token is written; PASS = rows grow during a live game.

## R-057 (3), items I own
- final-topics-32295b MISSING: the TheSports capture (capture.py pid 2489797, started 14 Nov 03:30:03Z) was stopped by Nick on 20 Nov 03:16Z ('no use', stop cited in P72 c849817814, a disk decision, not an edge result; Reviewer review 05:45Z); the tree was copied to the box by P101a (10 files, 34,906,107,252 B, checksum_exit=0 06:21:17Z 22 Nov, agent/status/P101a-stale-ship.md) and the VOL2 source was gone by 07:24Z; whether P101b deleted it is NOT verified. So: dead by design (Nick, 20 Nov 03:16Z), data on the box, not missing.
- pmsport (the NHL moneyline recorder pm_sport_books.js, written 20 Nov by the Goalserve thread, books.jsonl.gz last written 20 Nov 14:28Z): I do not own it. I cannot say who stopped it; the NHL recorder was never in my orders. Goalserve thread / IT to answer. The same fixed code serves NHL (default league nhl) after the same pre-flight.
