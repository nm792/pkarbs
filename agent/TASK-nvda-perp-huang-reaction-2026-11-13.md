# Task for the server agent: NVDA perp reaction to the Huang resignation (read-only history pull)

From: Claude in the "PK arbs" project, on Nick's instruction (13 Nov 2026). Status: OPEN. Deadline: post results by 08:00Z or say why not.

## Hard rules
- Public read-only market data only. No orders, no keys, no account. If a host refuses the server, STOP and write outbox/nvda-perp-blocked.md with the exact error. No workarounds.
- Raw pulls to /vol2/nvda-huang/, results note committed (small).

## Pull (all timestamps UTC ms)
Window: 2026-11-09 20:00Z to 2026-11-13 03:00Z.
1. Polymarket perps (docs.polymarket.com/perps, host api.perpetuals.polymarket.com):
   - GET /v1/info/instruments -> find the NVDA instrument (record id, symbol, and whether it exists; if none, say so).
   - GET /v1/info/mark-history?instrument_id=ID&interval=1s&start_timestamp=...  (page with `more`)
   - GET /v1/info/klines interval=1m (price + volume + trades)
   - GET /v1/info/trades and /v1/info/funding for the same window if available.
2. Comparison venue: Hyperliquid xyz NVDA perp, POST api.hyperliquid.xyz/info {"type":"candleSnapshot","req":{"coin":"xyz:NVDA","interval":"1m","startTime":..,"endTime":..}} (coin name may differ; list via perpDexs/meta).
3. Underlying: NVDA cash/extended-hours prices for the same window from any independent source you can reach (state which).
4. Event times: first-report time (UTC) of (a) the 9 Nov probe story, (b) the board-removal reports, (c) the 8-K/press release dated 12 Nov (EDGAR acceptance time). Cite the source for each.

## Output (outbox/nvda-perp-huang-2026-11-13.md)
For each event: price just before; price 1 s, 10 s, 60 s, 5 min, 30 min after; max move; time to reach 50% and 90% of the 30-min move; volume and trades in those windows; each venue side by side, plus the underlying when it was trading. Plain numbers, no interpretation. Note all gaps in the data.
