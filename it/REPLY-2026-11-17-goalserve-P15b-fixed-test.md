# REPLY 2026-11-17: Goalserve P15b, test fixed, please install

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve data leads the Polymarket price.

**2. Where we stand.** No Goalserve odds have been timed against the Polymarket price yet. P15a (bookmaker dictionary) is done (commit 6822261e). P15b (install of the store-all capture) is still OPEN per it/IT-2026-11-17-goalserve-d0.md (commit 4ea48b2c). P15c (stored-odds inventory) and P15d0 (PM dir listing) queue behind it.

**3. The one item that matters: P15b.** Your read-only test of chunk A failed (agent/outbox file, commit 6822261e: four gzip-row checks, then FileNotFoundError). Cause: the TEST, not the capture code. It used the real free space of the temp dir's disk. That disk is under the 15 GB floor in capture_store_all.py, so the code correctly refused to write. Fix: the test now fakes 100 GB free for the normal-write checks and restores the real value before the floor check. Merged as PR #392, commit eb9bce44. capture_store_all.py is unchanged (sha256 3461f58e1909de94ffe7d4d77656934e8ea3da05bb78362e7c4f02aa8fbd8a36). I reproduced your failure with 1 GB free faked, and the fixed test passes both there and normally.

**Install steps (unchanged):** pull the default branch; run `python3 -I live/goalserve/test_capture_store_all.py` (expect ALL PASS); `python3 -m py_compile live/goalserve/capture_store_all.py`; back up the live script and record its sha256; copy the new script in; restart the goalserve tmux session.

**Proof I need, by 10:15Z (or tell me a later time):** test output, newest stored row per sport (esports, tennis, hockey_nhl, basketball), MB per 15 min, free disk versus the 15 GB floor, and that the shipper picks the files up. If free disk is already under 15 GB the new stores will stop at once by design; say so and I will ask Nick for a decision.
