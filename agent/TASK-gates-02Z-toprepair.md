# Task for the server agent: 02Z again, with the exchange's top of book as a check and a repair

From: Claude in the "PK arbs" project (25 Oct 2026). Follows agent/PROTOCOL.md.
Status: OPEN

## The one question
Does our replayed book match the exchange's own best bid/ask, and does using it remove the crossed
books?

Background: the 02Z rerun passed every gate (thank you), but review found the replayed books are
often crossed: `crossed_checks=251326` in the rescan, and 4 of the 13 traded runs met a crossed leg
at match or unwind time (e.g. Jaiba Brava leg 1 bid 0.14 / ask 0.13). Polymarket books cannot be
crossed, so some of our levels are stale (most likely asks or bids taken by trades with no matching
price_change). Every price_change entry carries the exchange's `best_bid` and `best_ask` after the
change. `books.Replay` now compares our top with those on every entry (counts `top_mismatch`) and
drops our levels that the exchange says are gone. Both rescan.py and shadow_sim.py use it.
Tested locally: `python3 shadow/test_gates.py` gives 25 of 25; new case E7 opens a fake run without
the repair and none with it.

## Pass / fail (fixed before running)
- **PASS** if every real-mode gate passes on 02Z, including the two new ones:
  - G5: at every run's t0, every leg's best bid/ask equals the exchange's last reported best_bid/best_ask;
  - G5: no traded run meets a crossed leg at match or unwind time.
- **FAIL** otherwise: commit gates.txt and the fills CSV only, no per-run CSV, and stop.
- Either way, gates.txt must show the rescan line with `top_checks=`, `top_mismatch_before_repair=`,
  `levels_dropped=` and `crossed_checks=` (diagnostics, not gates).

## Steps (one process, same caps as last time)
1. `git pull`; `python3 shadow/test_gates.py` must end with "25 of 25 gates pass". If not, stop.
2. ```
   mkdir -p reports/sports-mece/gates-2026102502-top
   systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 \
     /usr/bin/time -v timeout 1800 python3 shadow/test_gates.py --real-data shadow/data-v2 \
     --hour 2026102502 --save reports/sports-mece/gates-2026102502-top/ \
     2>&1 | tee reports/sports-mece/gates-2026102502-top/gates.txt
   ```
3. On FAIL, delete `per-run-2026102502.csv` from the folder.
4. Clean up as before (no process left, /tmp/gates-* removed, `ps` and `free -m` appended).

## Report
Commit `reports/sports-mece/gates-2026102502-top/` and nothing else. Set Status above to DONE (or
FAILED) and commit. Claude reviews it before anything goes to Nick.
