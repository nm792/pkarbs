# Reply to IT: record each token's own books (PK arbs), 17 Nov 2026 09:40Z

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** no validated edge. The sports MECE NO side could not be tested because the recorder never stored a NO-token book (`shadow/shadow_logger.py` at 4c583cdfcc subscribed to YES tokens only). PR #393 fixes that; evidence below is from a 4-minute local smoke run, not a box run.
3. **The one item that matters most:** deploy PR #393 (branch `claude/project-thread-ua72b6`, commit f9139a777f) to the box logger and run it through live games, because it is the only way to see whether open NO books differ from 1 minus the YES book, as Nick says they do.

**What to run:** `python3 shadow/shadow_logger.py --out <dir on /mnt/HC_Volume_107257520>` (same flags as now). It now needs gzip on the gamma call (gamma returns HTTP 406 `gzip_required` for limit above 50; the previous code would have captured nothing), which the PR fixes. Output: `raw-*.jsonl.gz` now holds NO-token `book` and `price_change` frames unedited; `nocompare.jsonl` has one row per leg per 60 s resync (YES and NO best bid/ask each from its own stored orders, `y_ts`, `n_ts`, `mirror` flag). Expect roughly 2x the raw volume (the smoke run wrote about 2.6 MB gz per 4 minutes for 70 events, mostly pre-game); check the 15 GB floor and write only to the mounted volume.

**Test:** `python3 shadow/test_no_subscription.py` (6 checks) and `python3 shadow/test_gates.py` (25 of 25).

**Smoke result (17 Nov 09:31-09:35Z, inputs: gamma sports events starting within 8 h, 2052 assets, 6 WS connections; output not committed):** 36,812 `price_change`, 2,082 WS `book` and 15 `last_trade_price` frames received; 420 legs, 3,776 rows with a full top of book, YES/NO `mirror` True in all 3,776. These were mostly pre-game books and the replay mixes WS deltas with REST re-seeds, so this does not settle Nick's point on in-play books; the in-play run on the box does.

**Not done:** a NO-ask detector (the "no" run still prices from the YES mirror) and a planted-edge check on real files; both are for after in-play NO data exists.

Confidence 7/10 that the change records what is asked and runs; not verified on the box, and the in-play answer is unknown.
