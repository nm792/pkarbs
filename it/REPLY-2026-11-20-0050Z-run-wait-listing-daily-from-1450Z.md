# IT ask (UPDATED 20 Nov 01:00Z): run the gas listing waiter on the server, daily from 14:50Z (first run 20 Nov, for the 21 Nov event)

Goal: find and build un-publicised edges, target $500/day. Tonight's capture must show who sells the favourite at 0.70-0.85 about 7 minutes after listing (seen on 19 and 20 Nov). Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.

Measured position: only the 20 Nov event has a book capture from listing (15:01:02Z to 15:14:25Z, then my sandbox recorder stopped, cause UNVERIFIED). Artifact: /mnt/project-files/gas/20nov-listing-to-plus60-fav-bucket.md.

The one thing that matters: start `scan/gas_window/wait_listing.py` by 14:50Z on 20 Nov, not later.

DEPLOY BY SHA 0e113601dc1bad5a763b318044c9066002ce5ae6 (branch claude/project-thread-lfb1pf; it is NOT merged to the default branch yet because of a squash-merge conflict, so fetch this exact commit, do not use the default branch). This SHA adds pm_gas_trades.py, and wait_listing.py now starts it together with the books recorder.

Steps:
1. Run `python3 scan/gas_window/test_wait_listing.py`, `test_pm_gas_trades.py` and `test_gate_boundary.py`. Expect "2 of 2", "2 of 2", "5 of 5". Paste the outputs.
2. Run `python3 scan/gas_window/wait_listing.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --wait-until 2026-11-20T16:30:00Z --record-seconds 5400` from 14:50Z (10 GB free-space floor). It polls Gamma every 0.5 s, writes the detect time, then records at 1 s: all 12 books (6 buckets, YES and NO) in `<slug>.books.jsonl` and every trade of all six markets with wallet and tx hash in `<slug>.trades.jsonl`.
3. At 14:55Z paste the pid. At 15:15Z paste both file sizes twice, 60 s apart (growth). Say UNVERIFIED if any is missing.
4. Repeat daily. The AAA watcher (P54b/P54c) stays separate.

No orders are sent (A7).

Confidence 8/10: the tests pass locally; step 3 is the proof it runs on the server.
