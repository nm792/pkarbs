# Resting-bid backtest on LoL Worlds Game-1 markets (3 Nov 2026)

Question: if we rest rn1-style bids a few % under the market on past LoL games and hold to result, what do we earn?
Script: `sim_bids.py` (runs in ~10 s). Full table: `out_table.txt`, `out_bidsim.json`.
Data (already in repo): `../lag-study-worlds-2026-10/out/<match>/` = Riot livestats frames + all Polymarket data-api trades for 6 Worlds Game-1 markets (25-31 Oct). In-play only. ~$170k-$400k of public prints per game.

## Method (simulation on public trades)
- Bids on both tokens at ref x (1 - d). ref = trade-derived mid (avg of last bid-side and ask-side print) seen 1 s earlier.
- Filled when a public sell-direction print trades strictly through our bid; we get our price, up to 100 shares per print.
- Event cancel: no bids from event + 0 s / + 3 s to event + 30 s (event = livestats kill/tower/dragon/baron/inhib).
- "fair": ref replaced by the evrules LoL event model (leave-one-game-out beta) for 60 s after each event. "min": model may only lower our bids.
- Components per $ filled: entry = mid at fill - our price; 1-min move; 1-5 min move; rest to result. Sum = P&L before rebate. Rebate = 0.15 x 0.05 x p(1-p) (ESTIMATE).

## Results (computed from the simulation; rebates estimated)
| setup | d | fills | $ filled | entry | 1-min | entry+1-min | to result | rebate (est) |
|---|---|---|---|---|---|---|---|---|
| no cancel | 2.5% | 4,805 | $115k | +0.86% | -7.06% | -6.2% | -0.46% | +0.37% |
| cancel at event+3 s | 2.5% | 2,087 | $43k | +1.79% | -0.58% | +1.2% | +10.8% | +0.41% |
| cancel at event+3 s | 3% | 1,712 | $33k | +2.16% | -1.09% | +1.1% | +12.6% | +0.43% |
| model fair, cancel 3 s | 2.5% | 2,525 | $71k | -5.97% | -4.18% | -10.2% | -9.5% | +0.31% |
| model only lowers, no cancel | 2.5% | 2,922 | $66k | +1.97% | -2.82% | -0.9% | +9.0% | +0.38% |

Per game (cancel 3 s, d 2.5%), entry+1-min: -0.9%, +8.3%, +1.8%, -3.6%, +2.3%, -3.8%. To result: -36%, +57%, -77%, -57%, +11%, +44%.

## What it says
1. Without event cancels the bids lose 4-12% within a minute in all 6 games: most fills come from sellers reacting to game events.
2. Pulling bids for 30 s after each event brings the 1-min adverse move to ~0.6-1.1%, close to rn1's measured 1.6%, and entry ~1.8-2.2% (rn1 ~2.5%). This is consistent with rn1 avoiding event-driven fills. Net to 1 min ~+1.2% + ~0.4% rebate (est), but the sign varies game to game (3 of 6 positive).
3. Bidding off our LoL model loses ~10% to 1 min: model error (~4-6c median in the 60 s after events) is bigger than the discount. Use the model only to lower or pull bids.
4. To-result P&L swings +-35-99% per game (we accumulate the side that falls). With 6 games it is noise; do not read the totals as edge.

## Caveats
- Queue position ignored: we assume we are first at our price. Optimistic on fills, especially at small d.
- Mid is from prints (1 s timestamps), not the book. Real book captures (QFs 3-6 Nov) will replace it.
- Event cancel assumes we see livestats at the frame timestamp; real feed delay is unmeasured.
- 6 games, Game 1 only. Confidence 5/10.
