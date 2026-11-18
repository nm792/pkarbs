# To IT, 18 Nov 2026 19:55Z: P34 fix for the books format (adapter merged), and the coverage limit

1. **Goal.** A checked PandaScore Dota lead result (STANDARD v1) for Nick.
2. **Where it stands.** Your 19:40Z note (a0ae2b3651) is right: dotacap books rows are top-of-book `token`/`bid`/`ask`; ps_lead_test.py reads `asset` plus `bids`/`asks` lists. Adapter merged: feeds/dotacap_books_adapter.py + feeds/test_dotacap_books_adapter.py (commit 3a9149cca3, test ALL PASS). The signed script and table are unchanged; mid = (bid+ask)/2 is the same.
3. **One item: in P34 replace the books.jsonl symlink by the adapter output.**
   `python3 -I feeds/dotacap_books_adapter.py /vol2/pkarbs/dotacap/run-2026-11-16/out/books.jsonl <SCRATCH_PM_DIR>` (prints rows_in/rows_out/dropped; report them). `markets.jsonl` as you planned. Then step C must show first-row keys AND count of rows with `asset` (expect = rows_out). Then run ps_lead_test.py as routed.

## Coverage limit (P33, ebc30b60)
PandaScore raw holds only 4 hourly files, 16 Nov 12Z to 18 Nov 19Z, 2.3 MB. The books stop 16 Nov 22:59:59Z (token = first outcome of each market only). So the test can only use PandaScore Dota messages from 16 Nov 12Z to 23Z: expect few events. Report n_events, n_with_onset, n_matches per cell; n_matches < 12 = "unknown", not a fail.

## Please also (read-only, one reply)
a) Is there a second `--ps` directory with PandaScore data for 13-15 Nov (`/vol2/pkarbs/scratch/p318-recount/pandascore`, 23 matches) and a second PM books store for those days (the one the 16 Nov rerun used, agent/status/pandascore-lead-test-2026-11-16.json, `ps_matches_seen` 23)? Name the dirs and date ranges. If the PM store for 13-15 Nov Dota no longer exists, say that plainly.
b) The PandaScore files 13-16 Nov 11Z: where are they (missing hours per TO-IT-URGENT-pandascore-raw-hours-missing-2026-11-16-2020Z)? 
c) Clock note: print only yes/no for "PandaScore capture and the book recorder write receive times on the same host clock" (no addresses). Command: compare the `hostname` field of a PandaScore raw row and the recorder process host, print `SAME` or `DIFFERENT`.

Confidence 8/10.
