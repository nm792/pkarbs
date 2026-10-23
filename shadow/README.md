# Shadow logger for in-play sports MECE arbs

This places no orders and needs no account. It only uses public Polymarket endpoints
(gamma events, the CLOB `/books` endpoint and the market WebSocket).

## What it does

`shadow_logger.py` checks gamma every `--refresh` seconds for sports events that are
negRisk but not negRiskAugmented, and that started within the last `--window-h` hours.
It subscribes to the YES book of every leg, re-reads all books over REST every
`--resync` seconds, and writes:

- `raw-YYYYmmddHH.jsonl.gz`: every WebSocket frame and REST snapshot, with local receive time `r`
- `events.jsonl`: each event's legs, fee rate and `secondsDelay`, rewritten on every refresh, so delay changes in play are kept
- `runs.jsonl`: each stretch of time where the sum over legs of (ask + fee) is below `1 - min_edge`

`shadow_sim.py` replays the raw log. For each run it sends one limit buy per leg at the
ask seen at t0, sized to the thinnest leg (capped at `--max-usd`). Orders match at
t0 + `--one-way` + delay. If only some legs fill, the leftover legs are sold back at the
bid after another delay, with fees. The result is printed per delay value
(`market` uses each event's own `secondsDelay`).

## Run

```
pip install websockets
python3 shadow_logger.py --out data/            # runs until stopped
python3 shadow_sim.py --data data/ --one-way 0.05 --delays 0,1,3,market
```

For multi-day sampling, run it on an always-on host (London is closest to the CLOB)
under systemd or tmux. It uses about 1 MB of gzip per minute with 600 books.

## Known limits

- Fees use `feeSchedule.rate * p * (1 - p)` per leg, and only for markets with `feesEnabled`.
- The simulator assumes our order doesn't move anyone else's quotes and ignores queue
  position at the same price. Both make it optimistic.
- Unwinding sells leftovers at the bid. It doesn't try to buy the missing legs instead.
- `--lead-h` adds events that haven't started yet. Use it only for testing.
