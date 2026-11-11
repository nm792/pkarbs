# Question to the pkarbs owner: disk-gate ruling for tennis-books + oddspapi-multi (5 Nov)

From: the pkarbs agent, 2026-11-05 ~05:00Z.

Status: **BLOCKED — owner ruling required.** Not left "awaiting disk headroom" (that was a vague future state). Please rule on the disk gate so these either run or are closed.

## What is blocked
- **TASK-tennis-books-2026-11-05** (1 s tennis order-book recorder, 12 h): Nick Go 04:43Z was conditional on root `< 75% used` AND `>= 10 GB free`.
- **TASK-oddspapi-multi-2026-11-05** (45-min multi-sport odds pull): start if root `>= 10 GB free`.

## Current numbers
- Root `/` (sda1, 38 G total): **80% used, 29 G used, 7.4 G free**.
- Both gates unmet (need >= 10 G free; tennis also needs < 75%).
- Housekeeping can't reach 10 G free: stale `.bak/.pre`/backup tarballs under /root total ~0.4 G; the rest of /root (23 G) is live repo clones (mfw-clone 3.3 G, polymarket-temperature-trading 1.9 G, sports-maker 1.6 G, pkarbs 1.3 G, nautilus 1.0 G, etc.), not safely deletable by the agent.

## Ruling requested (pick one)
- **A. Relax the gate to >= 7 G free** -> the 45-min oddspapi-multi runs now; tennis-books runs on the same basis (or is dropped if it can't).
- **B. Approve a specific reclaim set** -> owner names what to delete/offload from /root to reach 10 G free; agent executes, then runs both tonight (14:00-23:00Z overnight window).
- **C. Mark both blocked / not-now** -> agent records BLOCKED and does not touch them until the owner re-queues.

Whichever you pick, the two tasks are recorded as BLOCKED pending this ruling (status files updated), so nothing is left on a vague "when disk clears."
