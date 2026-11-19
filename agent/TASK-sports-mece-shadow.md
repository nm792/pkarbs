# Task for the server agent: sports MECE shadow logging

From: Claude in the "PK arbs" project, on Nick's instruction (23 Oct 2026).
Status: OPEN

## Hard rules
- Shadow mode only. Do not place, sign or cancel any orders. Do not use wallet keys for this task.
- Public Polymarket endpoints only: gamma-api.polymarket.com, clob.polymarket.com/books,
  wss://ws-subscriptions-clob.polymarket.com/ws/market.

## What to run
1. `pip install websockets` (Python 3.10+).
2. Start the logger as a long-running service that restarts on failure (systemd or tmux):
   `python3 shadow/shadow_logger.py --out shadow/data/`
   Leave the defaults alone (in-play window 4 h, gamma refresh 120 s, REST re-sync 60 s, min edge 0).
   Do not pass `--lead-h`, which is only for testing.
3. Run it for at least 7 consecutive days, including a full weekend of European football.
4. Expect about 1 MB of gzip per minute while ~600 books are live. Keep the raw files; do not commit them.

## Daily report (commit to this repo)
Once a day, run:
`python3 shadow/shadow_sim.py --data shadow/data/ --one-way <measured one-way seconds> --delays 0,1,3,market --max-usd 500`
and commit `reports/sports-mece/YYYY-MM-DD.md` with:
- the simulator output lines;
- runs.jsonl line count, and the number of distinct events with a run;
- the top 5 runs by `(1 - cost0) * size0`, with title and `dur` (seconds the gap stayed open);
- any `secondsDelay` values seen on in-play events other than 0, 1 or 3;
- uptime and any errors from the logger output (ws errors, gamma errors, books errors).
For `--one-way`, use the measured one-way latency from the server to clob.polymarket.com (half a
`curl -w %{time_connect}` round trip is fine). Write down what you used.

## When done
Set Status above to DONE, commit, and say so in the report for the last day.
Code and background: shadow/README.md, notes/sports-mece-plan.md.
