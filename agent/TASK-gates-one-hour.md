# Task for the server agent: run the gates on one hour of fresh data

From: Claude in the "PK arbs" project (25 Oct 2026). Follows agent/PROTOCOL.md.
Status: DONE
Run this only after agent/TASK-STOP-scans.md is DONE.

## The one question
After the fixes in this commit, do the detector (`rescan.py`) and the fill simulator
(`shadow_sim.py`) see the same book on real data?

Background: in the clean rescan, at 2 ms latency 36 of 51 traded runs completed zero sets, even
runs that stayed open for over 100 ms. The cause in the code: `rescan.py` deduplicated raw
records on a key that is (None, timestamp, None) for current price_change messages, so different
changes in the same millisecond were dropped, and only the detector did that. It also opened runs
on legs with no full book after a gap, and the sim never added the rebate to P&L. Both programs now
use one shared replay (`shadow/books.py`). `shadow/test_gates.py` checks this on synthetic books
with hand-computed answers: 22 of 22 gates pass with the new code, and the old code fails the
same-millisecond, stale-book and rebate gates.

## Pass / fail (fixed before running)
- **PASS** if, on one hour, all of these hold:
  - G2: for every run, the detector's quote on every leg equals the sim's book at t0;
  - G2: at delay 0, at least 95% of the runs with dur > 0.05 s fill at least 95% of q on every leg;
  - G3: no run opened on a crossed or unseeded leg;
  - G4: the printed sim= totals equal the per-run CSV sums, and rebate_usd = R x fees_usd.
- **FAIL** otherwise. Do not run anything more. Report the failing gate and the low-fill examples.
- **NOT ENOUGH DATA** if the hour has fewer than 20 runs with dur > 0.05 s: then try the next older
  complete hour, at most 3 hours in total, one at a time.

## Steps (one process at a time)
1. `git pull`. Run `python3 shadow/test_gates.py` (synthetic, seconds, no data). It must end with
   "22 of 22 gates pass". If not, stop and report.
2. Pick the newest **complete** hour in `shadow/data-v2/` (not the one the logger is still writing).
3. Run, with a 2 GB memory cap and a 30 minute limit:
   `ulimit -v 2000000; timeout 1800 python3 shadow/test_gates.py --real-data shadow/data-v2 --hour <HOUR> --save reports/sports-mece/gates-<HOUR>/ | tee reports/sports-mece/gates-<HOUR>/gates.txt`
   (create the folder first). Do not touch the running logger.
4. If the result is FAIL, delete `per-run-<HOUR>.csv` from the folder (no P&L goes out on a
   failed gate) and keep `gates.txt`, `fills-<HOUR>.csv` and `runs-<HOUR>.jsonl`.
5. Clean up: confirm no test_gates/rescan/shadow_sim process is left running; temp dirs under
   /tmp/gates-* are gone; add `ps aux --sort=-rss | head -5` and `free -m` to `gates.txt`.

## Report (commit to this repo as soon as it finishes; it should take minutes, not hours)
Commit `reports/sports-mece/gates-<HOUR>/` (gates.txt, fills CSV, runs JSONL, and the per-run CSV
only on PASS). Write nothing else: no P&L summary. Claude reviews the CSVs run by run against
public price history before anything is reported to Nick.

Set Status above to DONE (or FAILED) and commit.
