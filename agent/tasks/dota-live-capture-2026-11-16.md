# TASK: Dota 2 feed-delay capture, 16-17 Nov 2026 (OPEN)

Owner thread: "Find a fast live Dota 2 feed". Same capture as agent/tasks/dota-live-capture.md (4 Nov), new config.

## Question (one only)
Do any Polymarket-listed Dota 2 leagues (1win Essence Playoffs: PARIVISION v Spirit, GamerLegion v LGD, LEGION v Aurora; DreamLeague Division 2 Playoffs; Asgard, EPC, EPL) run Valve spectator delays under 60 s? Measured per game as Valve game_state 6 time minus Polymarket game-winner price reaching 0.99/0.01 (livelag/lag.py).
BLAST Slam IX is 20-29 Nov (not 17 Nov: corrected from the Polymarket market text); config for it follows once Polymarket lists its games.

## Pass / fail
PASS (capture): realtime rows for at least 80% of in-game minutes for at least 4 series, and at least 80% of book polls 200 (404 on resolved markets does not count). FAIL: report why. Read-only, no orders.

## Run (one process, 400 MB cap)
```
cd agent/tasks/dota-live-capture-2026-11-16
OUT=$HOME/dotacap/out-2026-11-16; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=400M -p MemorySwapMax=0 timeout 90000 \
  node capture.js config.json $OUT 2026-11-16T08:30:00Z 2026-11-17T20:30:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
Copy $OUT to winmodels/raw/dotacap-2026-11-16/ (gz) every 30 min and at the end; clean up and write agent/status/dota-live-capture-2026-11-16.md.
