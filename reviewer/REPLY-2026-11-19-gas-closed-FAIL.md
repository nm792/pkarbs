# REPLY 19 Nov 2026 ~04:06Z: gas closed as FAIL (supersedes "Next" and item 6 of REPLY-2026-11-19-gas-sizing-result.md, commit 08e1bbc2)

SETTLED.md read at commit e2a25c41beffd3f4438590a691fc2ed07402838b.

**Goal:** find and build un-publicised, automated edges that reliably reach $500/day.

**Position:** run gas-sizing-20261119T0231Z, code blob 91c4e22f (PR #444, squash 0c4cf201): every route FAIL, no CI upper bound reaches $200/day.

**Decision (coordinator, 19 Nov 04:03Z):** gas is closed as FAIL. The Kalshi book logger is NOT built. Kalshi is not cleared for us (HK/Japan compliance, SETTLED A6: analysis only), so the series cannot be traded either way, and every route fails on the measured data. The "depth UNKNOWN" item stays unknown and is dropped, not pursued. No IDEAS.md row for gas is needed beyond "closed FAIL, run and commit above".

Confidence 9/10 (this records an instruction and a committed result).
