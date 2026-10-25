# Task for the server agent: rerun the gates on the same hour (02Z) with the fixed gate

From: Claude in the "PK arbs" project (25 Oct 2026). Follows agent/PROTOCOL.md.
Status: DONE

## The one question
Was the single G2 failure in `reports/sports-mece/gates-2026102502/` (1 of 92 runs, Real Salt Lake v
St. Louis, t0 1792894850.853) an artefact of how the gate took the t0 book, and does every gate pass
on 02Z once that and the corrupt-file problem are fixed?

## What changed in this commit (all tested locally: `python3 shadow/test_gates.py` gives 24 of 24)
1. **G2 t0 book by record, not by time.** The gate took the t0 book at `t0 + 1 µs`, which also
   includes later records that share the same millisecond receive time. `rescan.py` now stores
   `seq0` (the record that opened the run) and the gate rebuilds the book right after that record.
   New synthetic case E6 reproduces the failure with the old gate and passes with the new one.
2. **Corrupt hour files.** When the logger is killed and restarted, it appends a new gzip member
   after a truncated one; that is the "invalid block type" in 02Z, and `rescan.py` crashed on it
   (so the runs after 02:51 were lost and the open runs were never closed or deduplicated). The
   new reader (`books.read_lines`) skips the broken member and keeps reading the new one
   (synthetic gate G0). It reports `corrupt_members_skipped=`.
3. **Memory.** Real mode now copies only the event snapshots that hour needs (the last refresh
   before it plus the refreshes inside it), streamed, instead of the whole days-long events.jsonl.

## Pass / fail (fixed before running)
- **PASS** if all real-mode gates pass on 02Z: G2 quotes equal the book at t0 on every run; at
  delay 0, >= 95% of runs with dur > 0.05 s fill >= 95% on every leg; G3 zero crossed and zero
  unseeded; G4 CSV sums equal the printed totals and rebate_usd = R x fees_usd.
- **FAIL** otherwise: commit gates.txt and the fills CSV only, no per-run CSV, and stop.

## Steps (one process, under a memory cap and a time limit)
1. `git pull`; `python3 shadow/test_gates.py` must end with "24 of 24 gates pass". If not, stop.
2. ```
   mkdir -p reports/sports-mece/gates-2026102502-rerun
   systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 \
     /usr/bin/time -v timeout 1800 python3 shadow/test_gates.py --real-data shadow/data-v2 \
     --hour 2026102502 --save reports/sports-mece/gates-2026102502-rerun/ \
     2>&1 | tee reports/sports-mece/gates-2026102502-rerun/gates.txt
   ```
   Do not touch the running logger. If 1500M is not enough, stop and report the peak RSS; do not
   raise the cap on your own.
3. On FAIL, delete `per-run-2026102502.csv` from the folder.
4. Clean up: no test_gates/rescan/shadow_sim process left, /tmp/gates-* removed; append
   `ps aux --sort=-rss | head -5` and `free -m` to gates.txt. Keep `Maximum resident set size` from
   /usr/bin/time in gates.txt.

## Report
Commit `reports/sports-mece/gates-2026102502-rerun/` and nothing else: no P&L summary. Claude
reviews it run by run before anything goes to Nick. Set Status above to DONE (or FAILED) and commit.
