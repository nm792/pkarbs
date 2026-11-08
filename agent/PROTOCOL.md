# Protocol for server work (standing rule, from Nick, 25 Oct 2026)

The server is a shared resource. Every task in agent/ follows these rules. A task that breaks them
should not be run; report back instead.

1. **Local first.** Everything that can be tested without the server is tested without it first
   (synthetic books with hand-computed answers, small public samples). Code changes ship with tests:
   `python3 shadow/test_gates.py` must end with "N of N gates pass" before any server task uses that code.
2. **Small and bounded.** A server task gets at most 1-2 hours of data, streams files (no loading a
   whole data set into memory), runs one process at a time, and runs under a memory cap and a time
   limit on resident memory, e.g. `systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 timeout 1800 python3 ...`
   (`ulimit -v` caps virtual memory and kills Python early; do not use it). No overlapping jobs.
3. **One question, pass/fail fixed in advance.** Each task states the single question it answers and
   the pass/fail criterion before it runs. If a gate fails, stop, report the failure and the examples,
   and do not report P&L.
4. **Clean up.** When done, kill every process the task started, delete its temp files, and say so in
   the report (`ps` and `free -m` after).
5. **No queue.** Never start new server work while an earlier task's results are still unreviewed.
   Only one task in agent/ is OPEN at a time, apart from the always-on logger.
6. **Label every number.** Each figure in a report says whether it was computed by the sim on real
   data, computed on synthetic data, or estimated. Estimates are never reported as measured.
