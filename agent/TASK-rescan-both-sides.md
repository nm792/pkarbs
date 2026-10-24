# Task for the server agent: v2 logger, and rescan of the raw logs for both sides

From: Claude in the "PK arbs" project, on Nick's instruction (24 Oct 2026).
Status: OPEN

## Hard rules
- Shadow mode only. Do not place, sign or cancel any orders. Do not use wallet keys for this task.
- Public Polymarket endpoints only: gamma-api.polymarket.com, clob.polymarket.com/books,
  wss://ws-subscriptions-clob.polymarket.com/ws/market.

## Why
- The first logger checked one side only: buy every YES at the ask for under $1. It never checked
  buying every NO for under $(n - 1), which is the same as the YES bids, net of fees, adding up to
  more than $1. The NO book is the exact mirror of the YES book (checked live on 24 Oct: 92 of 92
  legs identical at full depth), so the YES books in the raw files already hold both sides.
- It had no check that the leg list was the whole event. When a leg closed (usually the winner),
  the remaining losers at 0.1c looked like a $1 set for 1c. The 24 Oct report's top 4 runs
  (cost0 0.005 to 0.020) are these, and they make up about $96.1k of the $96.4k "seen".
- The old simulator paired each run's quotes with the event's latest leg list, not the list at t0.

## What changed (shadow/)
- `shadow_logger.py`: checks both sides (runs.jsonl gets `side`, `payout`, `assets`, `n_markets`);
  skips events with a closed or missing leg; events.jsonl gets `no` token ids, `n_markets`,
  `complete`, `closed_legs`, `fee_exp`.
- `rescan.py` (new): replays old raw files through the new checks and writes a new runs.jsonl.
- `shadow_sim.py`: both sides; each run's own leg list; FAK per leg in non-atomic batches of 15;
  each leg's own secondsDelay for `market`; tick rounding; orderMinSize in USDC or shares
  (`--min-unit`); fee at each fill price with the fee exponent; unwind result shown separately;
  a cancelled-game line (moneyline/halftime sets pay $0 for YES, $n for NO) and EV at `--cancel-rate`.
- The previous versions are in git history at commit 688cb1a.

## What to run
1. Stop the logger and restart it on the new code, writing to a new directory so old and new
   runs are not mixed: `python3 shadow/shadow_logger.py --out shadow/data-v2/` (same defaults
   as before). Keep it running for the rest of the 7-day window.
2. Bring the closed-hour raw files back from the storage box next to the old events.jsonl
   (23 Oct 11Z onward, and the 02Z+ files from the volume). Skip the corrupt 01Z file.
3. `python3 shadow/rescan.py --data <old data dir> --out shadow/rescan/ --fetch-totals`
4. Run the simulator twice, once per min-size unit:
   `python3 shadow/shadow_sim.py --data <old data dir> --runs shadow/rescan/runs.jsonl --one-way 0.0019 --delays 0,1,3,market --max-usd 500 --min-unit usdc`
   and the same with `--min-unit shares`.

## Report (commit to this repo)
Commit `reports/sports-mece/rescan-2026-10-24.md` with:
- both simulator outputs, as printed (yes, no and both lines);
- for each side: run count, distinct events, runs with dur >= 1 s and >= 3 s;
- for each side: median and max edge per set in cents ((payout - cost0) * 100), and median size0;
- the top 10 runs per side by (payout - cost0) * min(size0, 500 / cost0), with title, legs,
  n_markets and dur;
- how many runs in the old runs.jsonl are not in the rescan (dropped as incomplete), with the
  leg counts over time for events 1162692, 1222536, 1237627 and 1222364;
- the `secondsDelay` values seen in events.jsonl (count of None, 0, 1, 3, other).
From then on, the daily reports use shadow/data-v2/ with the new simulator, in the same format.

## When done
Set Status above to DONE and commit.
