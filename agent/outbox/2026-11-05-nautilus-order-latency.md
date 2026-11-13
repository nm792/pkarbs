# outbox: nautilus order latency (read-only, no orders placed)

## RESULT
- Sources: Nautilus SpeedStrategy live Polymarket CLOB runs on this server — `/root/034_live.log` (run 2026-10-22 03:16-03:18Z), `/root/030_live.log` (run 2026-10-21), and the note-034 archive `mfw-clone/from_agent/data/034/live_20261022T031618Z/nautilus.log`. Order events carry wall-clock ISO + ns `ts_event`.
- 69 orders parsed across the runs; **30 with a strategy-submit -> venue-ack (`OrderAccepted`) delta**.
- submit->accepted: **n=30, median 0.206 s, p90 1.281 s, max 3.795 s** (percentiles on ns timestamps).
- cancel-send -> OrderCanceled: n=30, median 0.126 s, p90 0.318 s, max 2.408 s.
- submit -> canceled: n=30, median 0.302 s, p90 1.764 s, max 4.324 s.
- No `OrderFilled` rows in these limit-away runs (orders placed away and cancelled before fill); fill latency not measured.
- CLOB `/time` from this server, 20 curls same session: connect median 2.4 ms (p90 3.6 / max 4.3 ms); round-trip incl body (`time_starttransfer`) median 0.066 s, p90 0.081 s, max 0.084 s.

## DATA
- Raw per-order deltas (order-id prefix + deltas, no keys/addresses/signatures): `agent/outbox/nautilus-order-latency-2026-11-05.csv`.
- Source logs: `/root/034_live.log`, `/root/030_live.log`, note-034 archive `nautilus.log` (paths above; kept on disk, nothing altered, no orders placed/cancelled by me).

## OPEN / NOT VERIFIED
- No fill (#59042) latency: limit-away orders all cancelled before a fill -> no submit->fill sample in these logs. Fill latency needs a run that actually filled, or the tennis 1 s book run's own order timings.

## Count
tasks answered 1 (nautilus-order-latency), outstanding 0 for this item, PENDING open 0.
