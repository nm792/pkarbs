# rn1 raw data (pulled 29 Oct 2026)

Wallet `0x2005d16a84ceefa912d4e380cd32e7ff827875ea` (Polymarket @rn1). Public read-only endpoints only, no auth.

**Where the files are.** All files are in this folder and in the repo (`reports/rn1/raw/`), and verified against `SHA256SUMS`. Files 1-6 were copied byte-for-byte from the Composio sandbox (backup copy also at its `/mnt/files/rn1-raw/`).

Files 1-6 are the exact files the 29 Oct note (`../rn1-analysis-2026-10-29.md`) was computed from, found intact in the sandbox at `/home/user/rn1/`. File 7 is new.

| # | File | Endpoint and params | Pulled (UTC) | Rows | Notes |
|---|---|---|---|---|---|
| 1 | `act7d.json.gz` (75.9 MB raw) | `data-api.polymarket.com/activity?user=W&limit=500&start=a&end=b&sortBy=TIMESTAMP&sortDirection=DESC&offset=k`, 168 one-hour windows (`pull.py`) | 29 Oct 02:01-02:08 | 81,369 | List of response rows, de-duplicated on (txHash, asset, type, size, side, timestamp, price). Otherwise unmodified. |
| 1a | `act7d.json.log.gz` | per-window log for #1: start, end, rows | same | 168 windows | Max 1,688 rows in any window, none hit the 3,000 offset cap, so no window was split. |
| 2 | `act2h.json.gz` | `/activity`, same method, last 2 h | 29 Oct 02:02 | 615 | Probe pull, 00:02Z-02:01Z 29 Oct. |
| 3 | `pnl.json.gz` | `data-api.polymarket.com/v2/user-pnl`, `interval=all`, `fidelity=1d` (values echoed in the response) | 29 Oct 02:01 | 478 points | Unmodified response. Cumulative daily points 10 Jul 2025 to 29 Oct 2026 00:52Z. Fields include economic_pnl, trade_pnl, fees, fees_paid, fees_refunded, maker_rebate, taker_rebate, reward_income, yield/referral/sponsored income, volume, volume_usdc, trade_count, deposits, withdrawals. One step is not 1 day: the last point (29 Oct 00:52Z, partial day). |
| 4 | `meta_all.json.gz` (57.0 MB raw) | `gamma-api.polymarket.com/markets?limit=100&closed={true,false}&condition_ids=...` in batches of 40 (`dec.py`) | 29 Oct 02:09-02:12 | 8,086 markets | Dict conditionId -> unmodified gamma market object. Covers every condition traded in #1. 7,810 closed at pull time. |
| 5 | `mt.json.gz` | `data-api.polymarket.com/trades?user=W&limit=500&offset=0..2500&takerOnly={true,false}` (`mt.py`) | 29 Oct 02:07 | 3,000 + 3,000 | Dict {"true": taker-only fills, "false": all fills}. Capped at offset 2,500, so it covers only 25 Oct 14:59Z-29 Oct 01:59Z (taker) and 28 Oct 20:15Z-29 Oct 02:04Z (all). Superseded by #7. |
| 6 | `pos.json.gz` | `data-api.polymarket.com/positions?user=W&limit=500&sizeThreshold=1` (`pos.py`) | 29 Oct 02:04 | 500 | Open positions. **Truncated** at the 500 limit; not paged. |
| 7 | `trades7d.tar.gz` | `data-api.polymarket.com/trades?user=W&takerOnly={true,false}&limit=500&start=a&end=b&offset=k`, 168 one-hour windows per flag, same bounds as #1 | 29 Oct 03:14 (re-pulled from this container; an identical 03:05 pull in the sandbox gave the same counts and dollars) | 72,771 all + 5,634 taker | One JSON file per (flag, hour): {start, end, takerOnly, pulled_at, log, rows}. Rows unmodified. Script: `../rn1-scripts/pull_trades7d.py`. No window needed splitting, no errors. **Maker/taker per fill:** a fill is taker if it appears in the `takerOnly=true` set (match on txHash, asset, size, price, timestamp; all 5,634 taker rows match a row in the all-fills set), otherwise maker. |

Window for #1 and #7: `start=1792634632` (22 Oct 2026 02:03:52Z) to `end=1793239431` (29 Oct 02:03:51Z).

## Checks against the 29 Oct note
| Note says | Raw data shows | Match? |
|---|---|---|
| 81,369 activity rows | 81,369 | Yes |
| 72,749 fills, all buys | 72,749 TRADE rows, all BUY | Yes |
| 0 sells, merges, splits, conversions; 8,595 redemptions | Types: TRADE 72,749, REDEEM 8,595, REWARD 11, MAKER_REBATE 7, TAKER_REBATE 7. No SELL/MERGE/SPLIT/CONVERSION | Yes |
| Bought $18.0M | $17,996,351 | Yes |
| 8,086 traded markets with metadata | 8,086 conditions, 8,086 gamma objects | Yes |
| Lifetime $15.50M, trade +14.80M, fees -1.38M, maker reb +1.18M, taker reb +0.57M, rewards +0.33M, volume $692M, 5.07M fills | Last pnl point: 15,500,687 / 14,800,770 / -1,382,403 / 1,177,869 / 570,350 / 334,100 / 692,341,108 / 5,072,241 | Yes |
| Window "21 Oct 02:00Z to 29 Oct 02:00Z", "21 to 28 Oct" | Data runs **22 Oct 02:04Z to 29 Oct 02:03Z** (168 h) | **No**: the note's window label is one day early |
| Taker share 12.9% of dollars (83 h) | Over the full 7 days: 5,634 taker fills, $2,508,465 of $17,953,731 = **14.0%** of dollars, 7.7% of fills | **Differs** (different window; not explained here) |
| /trades all-fills count | 72,771 rows (72,748 unique) vs 72,749 activity TRADE rows | Near match; 23 duplicate rows in /trades, small residual difference not investigated |

## Gaps
- Activity and trades cover only the 7 days above, not further back. `/activity` and `/trades` both accept start/end windows, so going back further is cheap (about 20 s per week of trades).
- No on-chain order-filled events: the Goldsky orderbook subgraph still returned 429 at 03:04Z. Maker/taker comes from the `takerOnly` flag (#7), which is Polymarket's own field, not an on-chain check.
- No order book or price history for the traded markets, and no external odds feed.
- `pos.json` truncated at 500.
- Since 29 Oct 03:13Z this project's container can reach data-api and gamma-api.polymarket.com directly (Nick allowed them), so further pulls no longer need Composio.
- The pnl request URL was run by hand via `g.py`; params are taken from the response echo.
