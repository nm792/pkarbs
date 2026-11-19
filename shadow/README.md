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
- `runs.jsonl`: each stretch of time where a full set is underpriced, on either side:
  `side=yes` buys every YES at the ask (pays $1); `side=no` buys every NO (pays $(n-1)).
  The NO book is the mirror of the YES book (NO ask = 1 - YES bid; checked live on 24 Oct, 92 of 92
  legs identical at full depth), so the NO side is computed from the YES books.
  Events with a closed or missing leg are skipped (`complete` in events.jsonl).

`rescan.py` replays old raw files through the current checks, both sides, and writes a new runs.jsonl.

`shadow_sim.py` replays the raw log. For each run it sends one FAK buy per leg at the price
seen at t0, sized to the thinnest leg (capped at `--max-usd`), in non-atomic batches of 15.
Each leg matches at its send time + `--one-way` + delay (`market` uses each leg's own
`secondsDelay`). If only some legs fill, the leftovers are sold back at the bid after another
delay, with fees. It enforces tick and `orderMinSize` (`--min-unit usdc|shares`, since the docs
conflict), and prints each side and both combined, the unwind result, a cancelled-game line
(moneyline/halftime sets pay $0 for YES, $n for NO) and EV at `--cancel-rate`.

## Run

```
pip install websockets
python3 shadow_logger.py --out data/            # runs until stopped
python3 shadow_sim.py --data data/ --one-way 0.05 --delays 0,1,3,market
python3 rescan.py --data old_data/ --out rescan/ --fetch-totals   # old raw files, both sides
```

For multi-day sampling, run it on an always-on host (London is closest to the CLOB)
under systemd or tmux. It uses about 1 MB of gzip per minute with 600 books.

## Known limits

- Fees use `feeSchedule.rate * (p * (1 - p)) ** exponent` per leg, and only for markets with `feesEnabled`.
- The simulator assumes our order doesn't move anyone else's quotes and ignores queue
  position at the same price. Both make it optimistic.
- Buying NO needs no inventory. A NO on every leg can be merged to $(n-1) at once through negRisk
  conversion, or held to resolution.
- Unwinding sells leftovers at the bid. It doesn't try to buy the missing legs instead.
- Selling a leftover leg may not be possible until the trade is confirmed on chain, so the
  unwind is optimistic. A YES set is locked until resolution (no documented early merge).
- Cancelled-game handling picks market type from the title ("exact score" resolves 0-0; the rest
  resolve all No). Check new market types by hand.
- `--lead-h` adds events that haven't started yet. Use it only for testing.
