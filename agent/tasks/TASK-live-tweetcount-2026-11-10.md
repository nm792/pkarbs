# TASK: tiny live test of the weekly Elon tweet-count rule (UPDATED 05:25Z: one bracket per window)

Approved by Nick, 10 Nov 2026 05:12Z ("1. yes"); Nick then said "we only need to buy one bucket" (05:19Z). Hard cap, taker only, hold to resolution.

## Rule (locked, do not change)
- Weekly Elon windows only (title 'Elon Musk # tweets <date> - <date>', 7 days).
- Decision at T = window end minus 24 h. agent/tasks/tweetcount-decide.py prints at most ONE order intent (the single largest model-minus-ask edge over all brackets, YES or NO) and places nothing. It refuses to run outside [T, T+10 min] unless --force.
- Order: BUY only, marketable FOK/IOC limit at the printed ask (taker). NEVER resting orders, never sell, never market-make. Hold to resolution.
- First decision times: T = 12 Nov 17:00Z (window 6-13 Nov, slug elon-musk-of-tweets-november-6-november-13-2026); then 16 Nov 17:00Z (10-17 Nov) and every following weekly window. Windows already past their T are skipped.

## Hard caps (enforce in the executor, not only in the script)
- $5 per window (one bracket), $50 total (10 windows). Stop after 10 windows or when cumulative realised loss reaches $40, whichever first.
- Kill switch: if the file agent/KILL-LIVE exists on any branch, or Nick says stop, place nothing further.
- The key is the Polymarket trade-only session key (Nick authorised 4 Nov). It must have NO withdrawal permission; if it can, stop and say so.

## Steps for Hermes
1. Dry run now (no orders): `python3 agent/tasks/tweetcount-decide.py --slug elon-musk-of-tweets-november-6-november-13-2026 --force`. Before T the output is not a real decision (incomplete data); the dry run only proves the script runs, xtracker is reachable from the server and books load. Write output and any error to agent/outbox/live-tweetcount-dryrun-2026-11-10.md.
2. Arm a timer for each T (existing capped-pilot order path/Nautilus). At T..T+10 min run the script, check the intent against the caps, place it, log order id, fill price and size to /vol2/pkarbs/live_tweetcount/orders.jsonl and the outbox.
3. Report in agent/outbox/live-tweetcount-first-order-<date>.md when the first order is placed (or why skipped). After each window resolves, write realised P&L.
4. If xtracker is not reachable from the server, write that to the outbox and place nothing; the thread will supply the count another way.

Backtest of exactly this rule (one bracket, largest edge, $5 cap, 96 weekly windows): 82 bets, stake $311, P&L +$185 (+60%), placebo +$68 +-102; train +20% / test +108%. Expect about +$2 per window with a standard deviation of about $13, so a few dollars and very noisy. This is a check that live fills match the backtest, not a proof.
