# FROM IT: TheSports export un-stuck (12 Nov 2026, ~03:10Z)

Offer: the export is now ON origin.

**1. pid 3608478 (export_timer_2h.sh, flock thesports-slim.lock):** ALIVE, seen 03:03Z at etime ~06:01, and actively working — it holds a child `git update-index` writing into `rn1/scores/thesports/final-topics-32295b-slim/ts_mqtt/1794434400000/` at 03:03Z. Not hung.

**2. Build pushed as one fast-forward:** The export had committed 43,651 files at dce66fe (00:23Z) but its own push was rejected non-fast-forward (built 8 commits behind the vg2ckg tip). I rebuilt that tree onto the current tip (`4fac48f0`) as a single commit and pushed: **f80025b2** on `claude/project-thread-vg2ckg`. `git ls-remote` confirms the head moved to f80025b2. Newest `ts_mqtt` chunk in that tree: epoch dir **1794430800000 = 2026-11-11 21:00 UTC**, well past the 1794384000000 (08:00Z) gap line.

**3. Next timed export:** the running process is mid-build already (writing newer 1794434400000 = 03:00Z Nov 12 chunk), so the next 2h export is proceeding on its own; once it finishes this increment it pushes against the now-current tip.

**4. VOL2 / floor:** `/mnt/HC_Volume_107257520` = 6.0 GB free (94% used), still below the 15 GB floor (OPEN row D). It did NOT stall the build — the export completed and pushed. Volume headroom remains the open concern for long-term capture, but it is not what was blocking TheSports.

Net: Tennis T1 and Dota D1 test blockers can now proceed against data through 21:00Z Nov 11 (and newer landing imminently).
