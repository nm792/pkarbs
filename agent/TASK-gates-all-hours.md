# Task for the server agent: the same gates and sim on every clean hour of data-v2, one hour at a time

From: Claude in the "PK arbs" project (25 Oct 2026). Follows agent/PROTOCOL.md.
Status: DONE
agent/TASK-gates-02Z-toprepair.md is DONE with PASS 8/8 and was reviewed by Claude (25 Oct 07:45Z).

## The one question
Over every complete hour in shadow/data-v2/, what is the 1 s (each leg's secondsDelay) sim result,
split into its parts, and does it stay negative with more than the 9 trades of the 02Z hour?
(Resting on the slow leg is a separate simulation, not part of this task.)

## Pass / fail per hour (fixed before running)
An hour counts only if every real-mode gate passes for it (G2, G3, G4, G5). An hour that fails is
kept out of the totals: commit its gates.txt and fills CSV only, no per-run CSV. Do not stop the
loop for a failed hour; stop only if 3 hours in a row fail.

## Steps (strictly one hour at a time, never in parallel)
1. `git pull`; `python3 shadow/test_gates.py` must end with "25 of 25 gates pass".
2. Bounds: at most 12 hours (the 12 newest complete hours if there are more), and stop starting new
   hours after 2 h wall clock in total. Each hour took 7:40 and 198 MB at 02Z.
   List the complete hours in shadow/data-v2/ (every raw-*.jsonl.gz except the one the logger is
   writing). For each HOUR, oldest first:
   ```
   mkdir -p reports/sports-mece/hours/$HOUR
   systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 \
     /usr/bin/time -v timeout 1800 python3 shadow/test_gates.py --real-data shadow/data-v2 \
     --hour $HOUR --save reports/sports-mece/hours/$HOUR/ 2>&1 | tee reports/sports-mece/hours/$HOUR/gates.txt
   ```
   On a failed hour, delete that hour's per-run CSV. Commit after every 4 hours so progress is visible.
3. Clean up as before after the last hour.

## Report
Commit reports/sports-mece/hours/ and a one-line index `reports/sports-mece/hours/INDEX.txt`
(HOUR, PASS/FAIL, runs, traded at market delay, peak RSS). No P&L summary: Claude adds the totals
after reviewing. Set Status above to DONE and commit.
