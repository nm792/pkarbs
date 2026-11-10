# TASK: tiny live test of the weekly Elon tweet-count rule

Approved by Nick, 10 Nov 2026 05:12Z (his own message in the forecast-edges thread: "1. yes"). Hard cap, taker only, hold to resolution.

## Rule (locked, do not change)
- Weekly Elon windows only (title 'Elon Musk # tweets <date> - <date>', 7 days).
- Decision at T = window end minus 24 h. agent/tasks/tweetcount-decide.py prints the order intents (it places nothing). It refuses to run outside [T, T+10 min] unless --force.
- Orders: BUY only, marketable FOK/IOC limit at the printed ask (taker). NEVER resting orders, never sell, never market-make. Hold to resolution.
- First decision times: T = 12 Nov 17:00Z (window 6-13 Nov, slug elon-musk-of-tweets-november-6-november-13-2026); then 16 Nov 17:00Z (10-17 Nov), and every following weekly window. Windows already past their T (3-10 Nov) are skipped.

## Hard caps (enforce in the executor, not only in the script)
- $5 per bracket, $25 per window, $50 total open exposure across the whole test. Stop the test after 8 windows or when cumulative realised loss reaches $40, whichever first.
- Kill switch: if the file agent/KILL-LIVE exists on any branch, or Nick says stop, place nothing further.
- The key is the Polymarket trade-only session key (Nick authorised 4 Nov, see trading-key-rule). It must have NO withdrawal permission. If it can withdraw, stop and say so.

## Steps for Hermes
1. Dry run now (no orders): `python3 agent/tasks/tweetcount-decide.py --slug elon-musk-of-tweets-november-6-november-13-2026 --force`. NOTE: before T the output is not a real decision (it will use incomplete data); the dry run only proves the script runs, that xtracker is reachable from the server and that books load. Write the output and any error to agent/outbox/live-tweetcount-dryrun-2026-11-10.md.
2. Arm a timer for each T (use the existing capped-pilot order path/Nautilus; submit->ack is about 0.2 s). At T..T+10 min run the script, check every intent against the caps, place them, log order id, fill price and size to /vol2/pkarbs/live_tweetcount/orders.jsonl and the outbox.
3. Report in agent/outbox/live-tweetcount-first-order-<date>.md as soon as the first order is placed (or why it was skipped). After each window resolves, write realised P&L per bracket.
4. If xtracker is not reachable from the server, write that to the outbox and do NOT place orders; the thread will supply the count another way.

Pass/fail for the test is not a significance test: it checks that live fills and prices match the backtest (about +$100 per window on up to $25 of stake is NOT expected at this size; expect a few dollars). No re-picking thresholds.
