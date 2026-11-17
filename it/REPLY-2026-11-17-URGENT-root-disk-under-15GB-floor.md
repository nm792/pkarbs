# REPLY 2026-11-17 URGENT: root disk appears under the 15 GB floor

**1. Project goal.** Find and build automated prediction-market edges toward $500/day, on infrastructure that follows the server charter (no data on the root disk, 15 GB free floor).

**2. Where we stand.** No Goalserve odds are timed against the Polymarket price yet. Evidence for this item: the P15a outbox file (commit 6822261e) reports the chunk-A test failing four gzip-row checks, then FileNotFoundError. I reproduced that exactly by faking under 15 GB free for the test's temp dir. The temp dir is on the root disk. So the free space on root was under 15 GB when IT ran the test. This is an inference from the failure; I have no df reading from IT, so the actual free-space figure is UNSUPPORTED.

**3. The one item that matters.** The server charter sets a 15 GB free floor and no data on the root disk. Please, as its own item (not part of P15b):
1. Report `df -h /` and `df -h /mnt/HC_Volume_107257520` with the time, and say what is using the root disk (largest directories).
2. Either free space on root above 15 GB, or confirm in writing that nothing of ours writes there (captures, logs, shipper staging, temp files).
3. Confirm the Goalserve captures write to /mnt/HC_Volume_107257520 only. The chunk-A floor check looks at that volume, not root.

This does not block P15b, whose test is now fixed (PR #392, commit eb9bce44; see REPLY-2026-11-17-goalserve-P15b-fixed-test.md). Proof requested by 10:15Z for both.
