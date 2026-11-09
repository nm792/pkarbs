# Read-only: measured Nautilus order latency from existing logs (no new orders)

Nick says our Nautilus setup has shown ms-level order execution on tennis. We need that measured number for the tennis backtest. This is read-only: do NOT place, cancel or change any order, and do not touch any running capture.

Please, in one short round:

1. Find the Nautilus logs and any order records from real Polymarket runs on this server (for example under /root/nautilus, its logs/ or catalog/, or any systemd journal for a Nautilus node). List which files and dates you used.
2. For each order you find, take these timestamps (ns or ms as logged):
   - strategy submit (`SubmitOrder` / `OrderSubmitted`)
   - venue ack (`OrderAccepted`, or the POST /order HTTP response time)
   - for cancels: `CancelOrder` sent -> `OrderCanceled`
   - first fill (`OrderFilled`), if any
3. Write the deltas (submit->accepted, cancel->canceled) with median, p90 and max, and the count, to agent/outbox/2026-11-05-nautilus-order-latency.md. Also add 20 timings of `curl -s -o /dev/null -w '%{time_connect} %{time_starttransfer}\n' https://clob.polymarket.com/time` from this server.
4. Commit a CSV of the raw per-order deltas (no keys, no addresses, no signatures) to agent/outbox/nautilus-order-latency-2026-11-05.csv.

Pass: at least 10 submit->accepted deltas, or a clear statement that no Nautilus order logs exist on the server and where you looked. Never commit any key or secret.
