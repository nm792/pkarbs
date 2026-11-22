# IT to PK arbs, 20 Nov 2026 21:42Z: P87b held, live target needed

1. Goal: measure whether live feeds (PandaScore, Goalserve) lead Polymarket books by enough to trade.
2. Where it stands: the agent held P87b and made no change (TO-IT 21:15Z; pkarbs f18a7768, agent/outbox/P87b-goalserve-stop-basketball.md). VOL2 is under its 10 GB floor (9,612,718,080 bytes free at 21:00:00Z, trading-test data dialogue/status/DISK.tsv 17de161e); P97b (ship of your completed pmcs2 hours) is the top PK arbs row and has had no agent commit for 30 min at 21:42Z.
3. What matters most: P87 item 3 says to deploy live/goalserve/capture_store_all.py, but the agent reports the tmux goalserve process runs python3 live/goalserve/capture.py, and the local capture.py has uncommitted basketball polling/storage changes that differ from origin.

Ruling and what IT needs from you:
- IT agrees with the hold. P87b is now waiting (dialogue OPEN-WAITING, 21:42Z); nothing is restarted or edited.
- Please say, as a chunk: (a) which script the goalserve capture should run after the change (capture_store_all.py from PR 455, or capture.py); (b) what happens to the uncommitted local capture.py changes (keep a copy under VOL2 tmp, or discard); (c) the exact restart command; (d) how the agent confirms a quiet gap (the agent found provider update times stale in a basketball sample, so "between matches" is not verifiable from that feed alone).
- Order now: P97b, then P98 (dota smoke, read-only, now open), then P87b once you answer, then P68a.
