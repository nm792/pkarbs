# TASK: BLAST Slam IX Dota delay capture, 20-21 Nov 2026 (OPEN) + analyse the 16-17 Nov capture on the server

Owner thread: "Find a fast live Dota 2 feed".

## Part A: DROPPED (18 Nov). $HOME/dotacap/out-2026-11-16 no longer exists on the server (fd49c32afd); 16-17 Nov analysis not possible.

## Part B: BLAST Slam IX capture (starts 20 Nov 11:00Z)
Same read-only capture, config.json = the 6 BLAST Slam group games Polymarket lists on 20 Nov; add later days by re-running this config build when Polymarket lists them. Window 20 Nov 10:30Z to 21 Nov 00:30Z is 14 h, so timeout 57600 (16 h, covers start any time from 10:00Z through window end; never shorter than the window).
```
cd agent/tasks/dota-live-capture-2026-11-20
OUT=/mnt/HC_Volume_107257520/dotacap/out-2026-11-20  # DATA VOLUME, not $HOME; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=400M -p MemorySwapMax=0 timeout 57600 \
  node capture.js config.json $OUT 2026-11-20T10:30:00Z 2026-11-21T00:30:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
After the window, run: python3 lag.py $OUT config.json /mnt/HC_Volume_107257520/dotacap/out_lag_2026-11-20.json (same systemd-run limits) on $OUT with this config and commit only the result files. Clean up and write agent/status/dota-live-capture-2026-11-20.md.

## Data-safety checks (coordinator, 18 Nov)
1. Before 10:30Z 20 Nov: confirm `df -h /mnt/HC_Volume_107257520` has >=15 GB free and $OUT is on that mount (`df $OUT`).
2. IT check by 13:00Z 20 Nov (after the 11:00Z game ends): `ls -l $OUT` shows realtime.jsonl, books.jsonl, sportsws.jsonl, league_games.jsonl all non-empty and growing; reply in `it/` on branch `reviewer` with file names, sizes and row counts. Also run lag.py on the first game then and push the small result.
3. Repeat the size check at 18:00Z and 00:45Z. If any file is missing or stopped growing, say so at once.
4. Never rely on a copy to the storage box; the volume copy is the master. Do not delete $OUT until Nick says so.
