# 00-URGENT to IT, 20 Nov 2026 03:45Z (Goalserve thread; AMENDED 03:55Z: NHL ONLY, Nick dropped NBA, so no disk is spent on NBA). Start BEFORE the next puck drop.

1. **Goal:** record both tokens' own books for every NHL game moneyline, so the Goalserve hockey and basketball captures can be compared with Polymarket. **Disk:** written as gzip members, a few tens of MB per day (tested compression under 15% of raw); stops itself under 10 GB free (VOL2 was 14.85 GB at 02:47Z).
2. **Checked by me at 03:15Z (Gamma, live):** NHL had no games on 20 Nov (ET), the next NHL puck drop is 21 Nov 18:00Z (nhl-edm-car-2026-11-21, 14 games on 21 Nov); all moneyline markets accept orders, secondsDelay 1. Websocket could not be tested from my sandbox (blocked), so **step 3 below is the live proof**.
3. **Commands (one block, order matters; needs `node` 22 as for pm_cs2_books.js):**
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmsport; mkdir -p $D && cd $D
git -C /root/pkarbs fetch -q origin reviewer
for f in pm_sport_books.js test_pm_sport_books.js pm_cs2_books.js; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
node test_pm_sport_books.js      # must print PASS (7 checks...)
pgrep -f pm_sport_books.js || nohup node pm_sport_books.js $D 2026-12-31T00:00:00Z 10 >> stdout.log 2>&1 &
sleep 90; pgrep -f pm_sport_books.js; tail -5 recorder.log; ls -l $D; wc -l markets.jsonl
```
Paste the output under `## P86 NHL recorder (20 Nov)` in `agent/status/goalserve.md`. **Done check:** `recorder.log` shows `ws open, tokens N` with N > 0 (no `ws error` repeating), and `markets.jsonl` has lines.
4. **Protect the folder:** add `pkarbs/pmsport` to the ship_raw exclude list and the protected list (do not ship it, do not delete it).
5. **Live read, 30 min before each window (Nick's rule):** the first window is the NHL puck drop 21 Nov 18:00Z, so at 17:30Z on 21 Nov run and paste: `D=/mnt/HC_Volume_107257520/pkarbs/pmsport; pgrep -f pm_sport_books.js; tail -3 $D/recorder.log; ls -l --time-style=full-iso $D/books.jsonl.gz; sleep 120; ls -l --time-style=full-iso $D/books.jsonl.gz; df -B1 /mnt/HC_Volume_107257520 | tail -1` (file must GROW over the 120 s once a game is live; before the puck drop it may only grow slowly: say so, do not call it broken). Also do one read right after the 90 s start check, today. `it/goalserve_preflight.sh` now has a line for this recorder (pid plus recorder.log age under 700 s); use the latest copy.
6. **If step 3 fails:** paste `stdout.log` tail. I will fix and re-commit within 30 minutes.
