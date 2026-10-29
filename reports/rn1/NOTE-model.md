# rn1: what we're trying to learn, and the data behind it (29 Oct 2026)

This file is meant to stand on its own for a single review pass. Part 1 is the description, which is the coordinator's 02:36Z note with two corrections. Part 2 traces every figure in Part 1 back to a raw file and a script. Part 3 is the file index. It contains no new analysis.

Wallet `0x2005d16a84ceefa912d4e380cd32e7ff827875ea` (Polymarket @rn1). All data comes from public, read-only endpoints.

---

## Part 1. Description

**Objective.** Work out whether copying rn1's model would earn us about $50/day, reliably and without a catastrophic loss. Before any simulation we need to understand how its model really works, because skipping that step is the mistake we keep making with other accounts.

**What the data shows**

*Lifetime profit, July 2025 to 29 Oct 2026:* $15.50M
- Trading P&L: +$14.80M
- Fees: -$1.38M
- Maker rebates: +$1.18M
- Taker rebates: +$0.57M
- Liquidity rewards: +$0.33M
- Volume was $692M across 5.07M fills, so profit is about 2.2% of volume.

*Trend:*
- Profit per dollar traded has fallen from about 6% to 1-2%.
- The last 30 days averaged about $32k/day.
- 24% of days were losing days (116 of 477). *Correction: the earlier note said 26%.*
- The worst drawdown was $281k.

*How it trades, from 72,749 fills between 22 Oct 02:04Z and 29 Oct 02:03Z.* (Correction: the earlier note said 21-28 Oct.)
- **Buys only.** Every fill is a buy. There are no sells and no merges, and it holds everything to resolution.
- **Mostly resting orders.** 86.0% of its dollars are maker fills and 14.0% are taker fills. This covers the full 7 days and is confirmed on-chain: Polygon `OrderFilled` logs show exactly the same 5,634 taker transactions as Polymarket's `takerOnly` flag. (Correction: the earlier note said about 87% maker, based on 83 hours.)
- **Trades during games.** 93% of dollars go in after kick-off, mostly Counter-Strike 2, tennis and soccer.
- **Buys both sides, minutes apart.** Only 3% of dollars are filled within 5 seconds of a fill on the other outcome. 65% come 1-60 minutes later.

*Profit split over the 7 days, before fees:* +$296k
- Matched two-sided pairs: +$435k, a 3.9% margin.
- One-sided leftovers: -$139k.
- Rebates and rewards were 58% of September's profit.

**Questions to answer before simulating anything**
1. **Fair value.** What does it price against? An outside live feed (a sharp bookmaker or official data) that is faster than Polymarket, or Polymarket's own mid-price?
2. **Delay asymmetry.** Polymarket holds incoming taker orders for 1-3 seconds in sports, but resting orders can be cancelled during that hold. A maker with a fast feed can pull stale quotes before the taker's order lands. This may be the core edge, and it is the mirror image of why our 25 Oct taker test lost.
3. **Market mix.** Our 25 Oct verdict against market making used soccer trades only. rn1 leans on Counter-Strike and tennis, which are priced point by point, have fewer big jumps and have different delays.
4. **Quote placement.** How far from the best price it quotes, what size, whether it quotes both sides at once or one after the other, and how fast it requotes after a fill.
5. **Inventory.** Why does it buy the other side minutes later: a bet that the price will come back, or passive completion of the pair? What drives the -$139k on leftovers?
6. **Income stack.** How much comes from the bid-ask spread, how much from rebates and rewards, and which of those survive at our size. Rebates are shared in proportion to volume.
7. **Competition.** Its falling margin suggests copycats. What share of maker volume could we realistically win, given that the average maker earns about zero?

These questions are the coordinator's framing and may overlap a little: question 2 is one possible answer to question 1.

**Proposed order of work**
1. A one-page written model of rn1 for Nick to review.
2. A maker/taker split for every rn1 fill from on-chain records. *This is now done; see #8 in Part 3.*
3. A local simulation on made-up, hand-checked order books.
4. One bounded server job, run under PROTOCOL.md.

---

## Part 2. Where each figure comes from

Status key:
- **R** means I re-computed the figure from the raw file on 29 Oct at 03:35Z, in this project's container, using the script shown.
- **E** means the figure is taken from the earlier report (`rn1-analysis-2026-10-29.md`) and was not re-computed from raw.

All scripts are in `rn1-scripts/`. Files are in `raw/`, gzip'd, and must be unzipped to the names the scripts expect.

| Figure | Value | Raw file | Script or calculation | Status |
|---|---|---|---|---|
| Lifetime economic P&L | 15,500,687 | `pnl.json.gz` | last point, `economic_pnl` | R |
| Trading P&L | 14,800,770 | `pnl.json.gz` | last point, `trade_pnl` | R |
| Fees | -1,382,403 | `pnl.json.gz` | last point, `fees_paid` | R |
| Maker rebates | 1,177,869 | `pnl.json.gz` | last point, `maker_rebate` | R |
| Taker rebates | 570,350 | `pnl.json.gz` | last point, `taker_rebate` | R |
| Liquidity rewards | 334,100 | `pnl.json.gz` | last point, `reward_income` | R |
| Volume, fills | $692,341,108; 5,072,241 | `pnl.json.gz` | last point, `volume_usdc`, `trade_count` | R |
| Profit / volume | 2.2% | `pnl.json.gz` | 15.50M / 692M | R |
| First point (start date) | 10 Jul 2025 | `pnl.json.gz` | first point timestamp | R |
| Margin trend, 6% to 1-2% | Aug 2025 6.66%, Jan 2026 6.25%, Sep 0.73%, Oct 1.52% | `pnl.json.gz` | `a2.py`: month-end differences, economic_pnl / volume_usdc | R |
| Rebates + rewards share of Sep profit | 58% | `pnl.json.gz` | `a2.py` Sep row: (maker 166,585 + taker 150,900 + rewards 43,935) / 627,627 = 57.6% | R, see note A |
| Last 30 days mean/day | $31,814 (median 39,684, sd 47,022, 7 losing days) | `pnl.json.gz` | `a2.py` | R |
| Losing days | 116 of 477 daily steps = 24.3% | `pnl.json.gz` | daily differences of economic_pnl, count < 0 | R. **The earlier note's 26% does not match.** |
| Worst drawdown | -$280,792 | `pnl.json.gz` | `a2.py`, peak-to-trough on cumulative economic_pnl | R |
| Fills in 7 days | 72,749 TRADE rows, all BUY | `act7d.json.gz` | count by type and side | R |
| Window | 22 Oct 02:04Z to 29 Oct 02:03Z | `act7d.json.gz`, `act7d.json.log.gz` | min and max timestamp; 168 one-hour windows | R |
| No sells, merges, splits or conversions; 8,595 redemptions | as stated | `act7d.json.gz` | count by type: TRADE 72,749, REDEEM 8,595, REWARD 11, MAKER_REBATE 7, TAKER_REBATE 7 | R |
| Bought | $17,996,351 | `act7d.json.gz` | sum of usdcSize over TRADE rows | R |
| Fill sizes | median $37.5, p90 $642, max $22,616 | `act7d.json.gz` | sorted usdcSize | R |
| Taker share | 14.0% of dollars ($2,508,465 of $17,953,731); 5,634 of 72,771 fills | `trades7d.tar.gz` | rows with `takerOnly=true` vs all rows | R |
| Taker share, on-chain | 13.97% of dollars; same 5,634 taker txs; 1 tx on-chain only (`0x60a180cf…5608`) | `onchain_orderfilled.tar.gz` + `trades7d.tar.gz` | `pull_onchain.py`; role = taker if the `taker` topic equals the emitting contract; USDC = makerAmountFilled/1e6 | R |
| Earlier 87% maker (83 h) | 12.9% taker | `mt.json.gz` + `act7d.json.gz` | `a6.py` | E (superseded by the two rows above) |
| In-play share | 93.3% of resolved dollars after game start (pre <1 h 4.7%, pre 1-24 h 2.0%) | `act7d.json.gz` + `meta_all.json.gz` (`gameStartTime`) | `a4.py` timing table | R |
| Sport mix | CS2 19.4%, WTA 12.4%, ATP 11.7%, then soccer leagues and NFL | `act7d.json.gz` (`eventSlug` prefix) | `a4.py` category table | R |
| Gap to opposite-outcome fill | ≤5 s 3.0%, 5-60 s 16.3%, 1-10 min 41.6%, 10-60 min 23.7%, >1 h 5.9%, no opposite fill 9.5% | `act7d.json.gz` | `a5.py` (rows with no opposite fill fall outside a5's bins, so the bins sum to 90.5%) | R |
| Fill P&L before fees | +$295,914 on $17,816,359 resolved (1.66%) | `act7d.json.gz` + `meta_all.json.gz` (`outcomePrices`) | `a4.py` | R |
| Matched pairs | +$434,866 on $11,067,909 (3.93%) | same | `a4.py` | R |
| One-sided leftovers | -$138,952 on $6,748,450 (-2.06%) | same | `a4.py` | R |
| Resolved share | 99.0% of dollars (7,807 of 8,086 markets) | `meta_all.json.gz` | `a4.py`; outcomes as of the 29 Oct 02:09-02:12Z snapshot | R |
| Rebates and rewards paid in the 7 days | maker $41,344, taker $24,903, rewards $15,441 | `act7d.json.gz` | sum of usdcSize for those types | R |
| Leaderboard rank, $13.40M, 7-day +$360k | as in the earlier report | none saved | `/v2/leaderboard`, response not saved | E |
| FT / swisstony context | as in the earlier report | none | press summary | E |

**Note A.** `a2.py` prints its columns in this order: economic_pnl, trade_pnl, fees_paid, maker_rebate, taker_rebate, reward_income, volume_usdc, trade_count, unrealized_pnl. In the Sep 2026 row the values are 627,627 / 560,703 / -294,496 / 166,585 / 150,900 / 43,935 / 85.9M / 327,359 / -12,974. So maker rebates are 166,585, taker rebates 150,900 and rewards 43,935. The share is therefore (166,585 + 150,900 + 43,935) / 627,627 = 57.6%.

---

## Part 3. File index

All files are in `/mnt/project-files/rn1/` and in the repo at `reports/rn1/` on branch `claude/project-thread-ug2y74`. The repo puts scripts under `scripts/` instead of `rn1-scripts/`. Checksums are in `raw/SHA256SUMS`, and full endpoint details are in `raw/README.md`.

| # | File | What it is | Rows |
|---|---|---|---|
| 1 | `raw/act7d.json.gz` | `/activity`: all account events for the 7 days | 81,369 |
| 1a | `raw/act7d.json.log.gz` | per-hour pull log for #1 | 168 windows |
| 2 | `raw/act2h.json.gz` | `/activity`, a 2-hour probe on 29 Oct | 615 |
| 3 | `raw/pnl.json.gz` | `/v2/user-pnl`: cumulative daily P&L, fees, rebates, rewards, volume | 478 points |
| 4 | `raw/meta_all.json.gz` | gamma market objects for every traded market | 8,086 |
| 5 | `raw/mt.json.gz` | `/trades`, takerOnly true/false, capped at 3,000 each; superseded by #7 | 3,000 + 3,000 |
| 6 | `raw/pos.json.gz` | open positions, truncated at 500 | 500 |
| 7 | `raw/trades7d.tar.gz` | `/trades`, both takerOnly flags, 7 days, hourly files | 72,771 + 5,634 |
| 8 | `raw/onchain_orderfilled.tar.gz` | Polygon `OrderFilled` logs with rn1 as maker, 7 days | 72,772 |
| | `raw/README.md` | endpoints, parameters, pull times, gaps | |
| | `raw/SHA256SUMS` | checksums for files 1-8 | |
| | `rn1-analysis-2026-10-29.md` | the earlier full report (verdict, MECE P&L, comparison with past project conclusions) | |
| | `rn1-scripts/*.py` | `pull.py`, `dec.py`, `mt.py`, `pos.py`, `pull_trades7d.py`, `pull_onchain.py` (pulls); `a1`-`a6.py`, `tm.py` (analysis); `g.py` (HTTP helper); `gs.py`, `probe.py` (probes) | |

**Known gaps.** The data covers only these 7 days. There is no order book or price history, no external odds feed, and the leaderboard response was not saved. On-chain logs cover only fills where rn1 is the maker topic, which includes rn1's own taker orders. One transaction appears on-chain but not in the API, and it has not been investigated.
