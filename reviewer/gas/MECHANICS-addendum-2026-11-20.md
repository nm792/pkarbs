# MECHANICS addendum (20 Nov 2026): rows 5 and 7 of MECHANICS.md settled where the docs allow

Read 20 Nov ~00:55Z from docs.polymarket.com and clob.polymarket.com. Replaces the UNSOURCED marks in rows 5 and 7; changes no measured row.

| Row | Finding | Status | Source |
|---|---|---|---|
| 7a Taker delay (the 250 ms hold) | Applies only to \"selected crypto and finance up/down markets\"; check a market with `GET https://clob.polymarket.com/clob-markets/{condition_id}` and look for `itode: true`. The 20 Nov gas market's record (condition 0xe6cd93a3...dc1c3, token pair Yes/No) has no `itode` key: fields are r, t, c, mos 5, mts 0.001, mbf 1000, tbf 1000, ao, nr, cbos, aot 2026-11-19T15:00:26Z, ibce, fd {r 0.04, e 1, to true}, v v1. So the gas window has NO 250 ms hold. A sports-style game delay is configured only on sports markets. | PUBLISHED rule + MEASURED market record | https://docs.polymarket.com/concepts/order-lifecycle.md ; clob-markets call 20 Nov |
| 7b Order flow | EIP712-signed limit order, submitted to the CLOB operator which validates signature, balance, allowances and tick size; marketable orders match, others rest (GTC/GTD/FOK/FAK; post-only rejects if it would cross). Trade status path MATCHED, MINED, CONFIRMED (terminal) or RETRYING/FAILED; settlement is atomic on Polygon. During a delay window an order cannot be cancelled (does not apply to gas). Partial fills cannot be cancelled, only the rest. | PUBLISHED | order-lifecycle.md |
| 7c Price improvement | Price improvement always benefits the taker (resting 0.52 ask, buy at 0.55 pays 0.52). | PUBLISHED | order-lifecycle.md |
| 7d WebSocket events | Market channel publishes `book`, `price_change`, `last_trade_price`, `tick_size_change` and `best_bid_ask` events. No broadcast latency figure is published in the page read. | PUBLISHED (events) / latency UNSOURCED | https://docs.polymarket.com/market-data/realtime-data.md |
| 5 Queue priority | Not stated on prices-orderbook.md, order-lifecycle.md, matching-engine.md or prices-order-books.md; search of those pages found no price-time or FIFO statement. STAYS UNSOURCED. Consequence for the gate: no rule may assume a place in a queue; a resting bid is credited with a fill only when a recorded print crosses its price, never by queue position. | UNSOURCED | pages above |
| Matching restarts | Engine restarts reject order actions (HTTP 425), then two minutes of post-only mode. | PUBLISHED | https://docs.polymarket.com/trading/matching-engine.md |

ASSUMPTIONS.md changes: \"Latency send -> CLOB, 250 ms hold\" becomes: 250 ms hold = NOT APPLICABLE to the gas market (MEASURED market record); send-to-CLOB and ws broadcast latency stay UNSOURCED and are not used; queue priority stays UNSOURCED and is not used.
