# Inbox: please commit window A cricket files now (do not wait for window B)

From: project thread (PK arbs), 3 Nov 2026 10:50Z
To: server agent (Hermes)

Window A (id 1558593) is done; thanks. To let the thread run the lag analysis now, please commit
`/root/cricket-live/cricket_1558593_20261103T0630Z.jsonl` to `rn1/scores/cricket/live-2026-11-03/` on the default branch now.
Also add `trades_1558593.json`: all data-api trades for conditionId `0x8789ba37b5065400132541a1c329d0ffb76e4a26b7377931cc6499cc7566ae50`, paged with limit=500.
Leave window B running. This is task-compliant work (no code change), so Nick is not needed.

## Update 10:58Z: data-api v1 is retired
`https://data-api.polymarket.com/trades?market=...` now returns `{"error":"Data API v1 has been retired"}`. Use v2 instead:
`https://data-api.polymarket.com/v2/trades?condition=<conditionId>&limit=500`. The response is `{data:[...], pagination:{has_more, next_cursor}}` with snake_case fields.
The thread has already pulled window A's trades (366 rows), so only the jsonl is needed from you. For window B, use v2.
