# IT ask: run the gas listing waiter on the server, daily from 14:50Z (first run 20 Nov, for the 21 Nov event)

Goal: find and build un-publicised edges, target $500/day. The gas boundary rule needs the real order book in the first minutes after each next-day gas event lists (about 15:00Z), and my sandbox restarts, so the recorder must run on the server. Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.

Measured position: only one event (20 Nov) has a book capture from listing; first book 15:01:02Z, 804 snapshots to 15:14:25Z, then my sandbox recorder stopped (cause UNVERIFIED, likely a sandbox restart). Artifact: scan/gas_window/fixtures/gas20_books_two_snapshots.json at commit ff59768e08c6e61fa8a8f6b7e9c297e84f90aede.

The one thing that matters: please start `scan/gas_window/wait_listing.py` by 14:50Z on 20 Nov, not later.

Steps (deploy committed code by SHA ff59768e08c6e61fa8a8f6b7e9c297e84f90aede on branch claude/project-thread-vg2ckg, never edit it on the server):
1. Run `python3 scan/gas_window/test_wait_listing.py` and `python3 scan/gas_window/test_gate_boundary.py`. Expect "2 of 2" and "5 of 5". Paste both outputs.
2. Run `python3 scan/gas_window/wait_listing.py` from 14:50Z with output on /mnt/HC_Volume_107257520 (10 GB free-space floor). It polls Gamma every 0.5 s through errors, writes `<slug>.listing.json` with the detect time, then starts pm_gas_books.py at 1 s.
3. At 14:55Z paste the pid, and at 15:15Z paste the file size twice, 60 s apart (growth). Say UNVERIFIED if either is missing.
4. Repeat daily; the AAA watcher (P54b/P54c) stays separate.

No orders are sent (A7). Captured books are data only.

Confidence 8/10: the waiter's tests pass locally (2 of 2), but it has not yet run on the server; step 3 is the proof.
