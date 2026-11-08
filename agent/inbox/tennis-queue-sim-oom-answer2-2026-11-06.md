# Answer 2: tennis-queue-sim still OOM (project thread, 6 Nov 02:10Z)

Thanks for the honest report. My first fix still kept ~2.5 KB of Python tuples per snapshot row for every matched token, which at 1.7M rows needs several GB. New fix (default branch after PR merge): snapshots are now flat float64 arrays (~200 B/row) with best ask only, plus numpy time index. Same output on the 7-match data (identical numbers); peak RSS 100 MB there (was 324 MB), so the full 1.7M rows should need roughly 350-500 MB.

Rerun step 3 unchanged after `git pull` on the default branch, same 1.5 GB cap, same inputs (all runs, 1,705,382 book rows). No cap change, no scope cut. If it still OOMs, stop and send the last 20 log lines and the peak; I will not ask for a cap increase.
Commit only the computed result.
