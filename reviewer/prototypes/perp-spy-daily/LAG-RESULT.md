# Lag check result (exploratory, descriptive only; rule `LAG-RULE.md`, code `lag.py`, output `lag_result.json`)

**Data limit first.** The only minute S&P data this container can reach is the Hyperliquid xyz:SP500 1 m candles saved in pkarbs (12 Nov 21:38Z - 16 Nov 08:58Z). That gives one full SPY event (13 Nov) and the weekend part of 16 Nov. Blocked from here (connect refused by the egress proxy, 19 Nov ~02:40Z): api.hyperliquid.xyz, api.perpetuals.polymarket.com, query1/query2.finance.yahoo.com, fapi.binance.com, api.bybit.com, okx, kraken, bitget, mexc, gate, coinbase, api.polygon.io, stooq.com, cmegroup.com, alphavantage, twelvedata, tiingo, finnhub, financialmodelingprep, nasdaq. **Host to allow for the full test: `api.perpetuals.polymarket.com`** (Polymarket perps, 1-second mark history back to Aug 2026, used in pkarbs `weekend-perps/backfill-2026-11-16/pm.py`). `api.hyperliquid.xyz` as well for the live read (its 1 m candles only reach back ~5,000 minutes).

## 13 Nov SPY event (387 Polymarket prints, $13.7k taker buying)
- 28 perp moves of >= 10 bp in 5 min; 21 measurable (7 had no Polymarket print in the 10 minutes before).
- Time from the move until a Polymarket print had covered half the model's probability jump (seconds): 15, 16, 43, 55, 64, 76, 78, 84, 88, 112, 135, 231, 282, 463, 478, 517, 622, 643, 1066, 1495, and 1 still not there after 30 min. **Median 135 s; 5 of 21 within 60 s; 10 of 21 over 4 min.**
- This is time to the next trade at a caught-up price, not time for the quotes to move. Prints arrive about every 2-3 minutes, so much of the measured lag is waiting for a trade. The book may have moved sooner. Measuring quote lag needs book snapshots (live logger).
- Taker buys below the perp-implied fair value by more than fee + 1c: 88 prints, $2,648 (19% of taker buying). Realised at resolution: +$2,150. 13 Nov closed Down and most of these were Down buys, so one day's outcome drives the sign.

## 16 Nov (weekend part only, to Mon 08:58Z; 69 prints, $870 taker buying)
- 3 measurable moves, none caught up within 30 min (quiet weekend book).
- Stale buys: 12 prints, $107, realised -$51.

## What it says
On the one weekday available, Polymarket prints lag a 10 bp perp move by a median of about 2 minutes, and about a fifth of taker dollars traded at prices the perp already made stale. At November volumes that pool is roughly $2.6k/day of notional. The direction of the P&L can't be judged from one day. The full test (all ~75 events since Aug, second-level prints vs 1 s perp marks) needs `api.perpetuals.polymarket.com` allowed.
