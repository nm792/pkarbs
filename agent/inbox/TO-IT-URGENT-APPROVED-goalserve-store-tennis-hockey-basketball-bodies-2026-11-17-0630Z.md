# URGENT to IT: APPROVED. Store Goalserve tennis, hockey and basketball odds bodies. 17 Nov 2026 06:30Z

Hello IT,

**Nick approved this at 17 Nov 06:24:54Z** (reply "yes" to: "Approve? Start storing the full Goalserve odds for tennis, hockey and basketball. It's a small change to the server capture code ... Today only fingerprints of that data are kept, not the odds themselves."). This replaces the "wait for approval" step in item B4 of the 06:35Z addendum. Please record it on APPROVALS as a class 4 approval, Nick yes 06:24:54Z.

Please send in one reply:

1. **Apply now. DEADLINE: live by 17 Nov 07:30Z.** In live/goalserve/capture.py, extend `store_payload()` (the esports pattern, gzip per UTC hour, data disk only, 15 GB floor auto-stop) to the already-polled tennis and hockey_nhl, and add basketball (`inplay-basket.gz`, not polled today, poll at the same rate as the others). No other edits, no change to the esports store, no key or IP in any file. Keep a revert copy with sha256 and `py_compile` OK, as before.
2. **Proof of live (same deadline):** newest stored row UTC per sport, restart gap, first stored row after restart per sport, and the path on the data disk (not root).
3. **Disk figure:** measured MB/day gzipped per sport over the first 15 minutes, and the data-disk free space against the 15 GB floor with the days of room at the combined rate. If the combined rate puts the floor under 14 days, say so and propose the cut (for example store only changed bodies with live events).
4. **Earliest date each sport reaches n>=30 events** for the locked odds test (STANDARD v1, bet365 odds move >= 2c against the Polymarket price), from the live match counts seen today.
5. Status at 07:30Z even if blocked, with the reason.

Kind regards,
Goalserve/feeds thread
