# Reply to IT: shadow logger restart approved by Nick (17 Nov 2026 14:40Z)

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** no validated edge; the sports MECE NO side is untested because no NO-token book has ever been recorded. PRs #393 and #394 (merged, `claude/project-thread-vg2ckg`, 2e92b5c9c5) add it; offline tests only.
3. **The one item that matters most:** P16 may now START. Nick tapped "Yes, restart it" on the card "Restart the sports shadow logger, with NO tokens recorded, on the box?" at 14:36:23Z, which lifts the 3 Nov "do not restart" for this logger, new code only.

**Run exactly as in `it/REPLY-2026-11-17-shadow-logger-chunk.md`:** update the repo to `claude/project-thread-vg2ckg` at or after 2e92b5c9c5; `python3 shadow/test_no_subscription.py` and `python3 shadow/test_gates.py` must show ALL PASS and 25 of 25 before starting; then systemd-run scope `pkarbs-shadow-logger.scope`, `python3 shadow/shadow_logger.py --out /mnt/HC_Volume_107257520/pkarbs/shadow/data-v3/` (defaults, no `--lead-h`), output on the volume only, nothing on root. Watch: stop and tell us if the volume falls under 15 GB free. Proof for us: the first `nocompare.jsonl` rows and `raw-*.jsonl.gz` size after 10 minutes, and the `done`/error lines (any `gamma error` or `ws error`).

Confidence 9/10 that this is Nick's approval and the scope of it (his tap, the card text above); unknown until it runs: whether the box has python websockets and gamma access.
