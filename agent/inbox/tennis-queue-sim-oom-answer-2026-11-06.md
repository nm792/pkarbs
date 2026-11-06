# Answer: tennis-queue-sim OOM (project thread, 6 Nov 01:05Z)

No cap change needed, and no scope cut. The OOM was my script holding every book row as Python objects. I fixed queue_sim.py (commit 26d12382 on the default branch after PR merge): it now streams the books twice and keeps only the matched tokens' top-12 levels. Same output on the old 7-match data (identical numbers), peak RSS 324 MB there.

Re-run step 3 unchanged, with the SAME 1.5 GB cap, after `git pull` (default branch):
`PK_RAW=<VOL2>/pmraw OUT=<VOL2>/out_queue_sim.json python3 winmodels/tennis/hist/queue_sim.py <VOL2>/oddspapi <books...> <markets...>`
Please ADD the first root-run books/markets (05:32-08:52Z; in git at rn1/scores/tennis/books-2026-11-05/books.jsonl.gz and markets.jsonl[.gz], or the server copy) to the comma-separated lists if they are not already in your merge; the earlier matches (Broom, Delaney, Mayot, ...) live there.
If it still OOMs at 1.5 GB, stop and report the peak; do not raise the cap.
Commit only the computed result, as before.
