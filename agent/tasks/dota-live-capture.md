# TASK: live Dota 2 feed-delay capture, 4 Nov 2026 (OPEN, run today)

Owner thread: "Find a fast live Dota 2 feed" (branch claude/project-thread-gexs0s). Written 4 Nov 05:50Z.

## Question (one only)
For the 11 Polymarket-listed Dota 2 series on 4 Nov (config.json: Asgard, EPL Masters, Esports Pro Circuit, Media Eleague; first at 10:00Z, last at 19:00Z),
how many seconds after (or before) each Valve realtime event (kill-score change, tower/barracks loss) does the Polymarket game-winner price move?
The Valve endpoints were found 4 Nov 05:45Z and need no key: www.dota2.com/webapi/IDOTA2League/GetLiveGames/v001 and
www.dota2.com/webapi/IDOTA2MatchStats/GetRealtimeStats/v001?server_steam_id=<id> (kills per player, net worth, buildings).
They are blocked in the Claude sandbox, so this has to run on the server.

## Pass / fail, fixed before running
- PASS (capture): at least 4 of the 11 series have realtime.jsonl rows for at least 80% of their in-game minutes, and at least 80% of book polls return 200 (no 429 storms).
- FAIL: fewer than 4. Report which series failed and why (e.g. 403 from dota2.com, game not in GetLiveGames). No lag figures then.
- No P&L, no orders. Read-only capture.

## Run (bounded, one process)
```
cd agent/tasks/dota-live-capture
OUT=$HOME/dotacap/out-2026-11-04; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=400M -p MemorySwapMax=0 timeout 47000 \
  node capture.js config.json $OUT 2026-11-04T09:45:00Z 2026-11-04T22:45:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
- Load: dota2.com GetLiveGames every 5 s, GetRealtimeStats every 2 s for at most 10 live league games (about 5 req/s to Valve),
  OpenDota every 30 s, Polymarket CLOB /book every 2 s for at most ~15 tokens of series inside their window, Polymarket sports WS.
- First check (10:00Z): `tail $OUT/capture.log` and `wc -l $OUT/*.jsonl`. If dota2.com returns 403/429 repeatedly, kill the process and report.
- Copy $OUT/* to /mnt/project-files/winmodels/raw/dotacap-2026-11-04/ (or commit to winmodels/raw/dotacap-2026-11-04/ in this repo) every 30 min, not only at the end.
- Clean up at the end: confirm the node process is gone (`ps`, `free -m`) and say so in agent/status/dota-live-capture.md.

## Local test (done 4 Nov 05:42Z in the Claude sandbox)
- Mock Valve server: league_games, realtime (deduped on match.timestamp), rt_polls rows written correctly.
- Real Polymarket CLOB /book and sports WS: rows written (sports WS already carries Dota: "Yangon Galacticos v Resp Gaming", score "000-000|1-0|Bo3").
- Real dota2.com not reachable from the sandbox (proxy refusal); reachable via an outside fetcher (JSON confirmed).

## Report to agent/status/dota-live-capture.md
Row counts per file, number of series seen in GetLiveGames, 403/429 counts, process cleanup. The owner thread does the lag analysis.
