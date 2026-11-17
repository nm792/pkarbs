# TASK: BLAST Slam IX Dota delay capture, 20-21 Nov 2026 (OPEN) + analyse the 16-17 Nov capture on the server

Owner thread: "Find a fast live Dota 2 feed".

## Part A: analyse the 16-17 Nov capture locally on the server (first, it is quick)
The 16-17 Nov raw data never reached the repo (storage-box copy failed; the 90,000 s timeout in my task file was my mistake, the window needed 129,600 s). The local JSONL files still exist, so run the analysis there and push only the small result.
```
git pull; cd winmodels/dota/livelag
systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 timeout 1800 \
  python3 lag.py $HOME/dotacap/out-2026-11-16 ../../../agent/tasks/dota-live-capture-2026-11-16/config.json /root/out_lag_2026-11-16.json > /root/out_lag_2026-11-16.txt
```
Copy out_lag_2026-11-16.json and .txt to winmodels/dota/livelag/ and commit them (a few KB). Single process, no raw data in git.
Question: for each paired game, Valve game end (game_state 6) minus Polymarket game-winner price reaching 0.99/0.01, grouped by league. Pass: output produced. If lag.py errors, push the error text.

## Part B: BLAST Slam IX capture (starts 20 Nov 11:00Z)
Same read-only capture, config.json = the 6 BLAST Slam group games Polymarket lists on 20 Nov; add later days by re-running this config build when Polymarket lists them. Window 20 Nov 10:30Z to 21 Nov 00:30Z is 14 h, so timeout 54000 (not 90000).
```
cd agent/tasks/dota-live-capture-2026-11-20
OUT=$HOME/dotacap/out-2026-11-20; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=400M -p MemorySwapMax=0 timeout 54000 \
  node capture.js config.json $OUT 2026-11-20T10:30:00Z 2026-11-21T00:30:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
After the window, run Part A's lag.py command on $OUT with this config and commit only the result files. Clean up and write agent/status/dota-live-capture-2026-11-20.md.
