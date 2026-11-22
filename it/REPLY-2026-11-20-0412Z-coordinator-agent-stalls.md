# IT: the server agent keeps idling while rows are open. Fix the dispatch and wake jobs, and name the root cause (Nick, 20 Nov 04:10Z: "tell IT")

Goal: find and build un-publicised Polymarket edges, automated, toward $500/day. Settled rules: SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b.

Measured position: $0/day. The first lead candidate is PandaScore CS2 kill events preceding Polymarket trades in 2 of 3 sampled matches (exploratory, commits 3ac198c17c and 256853dbf1); it cannot be tested further until the rows below run.

**The one item that matters most:** the server agent idles while rows are open. Idle windows seen (UTC): 21:38 to 23:08 on 19 Nov, 00:23 to about 01:59 on 20 Nov, and again after the 03:05Z heartbeat on 20 Nov. Please (a) fix the dispatch and wake jobs so the agent never idles while an open row exists in it/ or reviewer/OPEN-ORDERS.md, and (b) name the root cause in a REPLY (what stopped the agent, what restarted it, which job should have woken it). A fix without a named cause does not count.

## Run order (do 1 to 6 in this order; paste the output of each as soon as it exists)
1. **Stop the TheSports writer now.** Nick ruled TheSports out on 19 Nov; the volume has 11-12 GB free against the 10 GB floor. Paste the pid that was stopped, and `df` for the volume before and after.
2. **PandaScore: export ALL CS2 matches row.** Paste the output path, row count and file size.
3. **PandaScore: fields check and discovery-fix deploy row.** Deploy by committed SHA only (never edit on the server) and paste the SHA, the test output and the fields check result.
4. **P86 NHL recorder, running by 06:00Z.** Paste the pid at 06:00Z and file size twice, 60 s apart.
5. **P86a gas listing waiter, running by 14:30Z today (earlier than the 14:50Z in my earlier note).** Deploy SHA 0e113601dc1bad5a763b318044c9066002ce5ae6 (branch claude/project-thread-lfb1pf; fetch that exact commit). Run the three tests first (test_wait_listing.py "2 of 2", test_pm_gas_trades.py "2 of 2", test_gate_boundary.py "5 of 5") and paste the outputs. Start `scan/gas_window/wait_listing.py --slug us-gas-price-on-november-21-2026 --out /mnt/HC_Volume_107257520/gas --wait-until 2026-11-20T16:30:00Z --record-seconds 5400`. Paste the pid at 14:55Z, and both file sizes (`.books.jsonl` and `.trades.jsonl`) twice, 60 s apart, at 15:15Z. Say UNVERIFIED if any is missing. Full instructions: it/REPLY-2026-11-20-0050Z-run-wait-listing-daily-from-1450Z.md at 7fe9999f.
6. **P87 coverage scan.** Paste the output path and the count of matches covered.

No orders are sent (A7). Never commit from /root/pkarbs (19 Nov deletion incident, PR 438/439).

Confidence 8/10: the stall windows and the order list come from the coordinator and the earlier IT notes; the root cause is unknown until IT names it.
