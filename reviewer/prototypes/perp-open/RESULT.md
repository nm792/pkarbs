# RESULT: perp vs Polymarket SPX "Opens Up or Down" (Reviewer prototype, 19 Nov 2026)

Rule: `LOCKED-RULE.md`, committed 47889d5b before any score. Code: `score.py`. Inputs: `data/` (Polymarket gamma + data-api v2 trades pulled 19 Nov 02:10-02:25Z by `fetch_pm.py`; Hyperliquid xyz:SP500 1 h candles and ^GSPC Yahoo daily bars copied from pkarbs main d9f9f905 `weekend-perps/backfill-2026-11-16/data/`). Output: `result.json`, `rows.json`. Rerun: `python3 -I score.py` in this folder.

## Verdict (locked): UNDERPOWERED, and it cannot reach the $200/day bar at current size
- TEST (1 Aug - 13 Nov, 74 days): 7 trades, hit 71%, realised +0.23 per share (CI +0.01 to +0.48), **$5.5/day (CI $0.1 to $14.3)** at 10% of the taker flow. Rebates $0.02/day.
- TRAIN (22 Apr - 31 Jul, 68 days): 13 trades, +0.06 per share (CI -0.11 to +0.24), $10.0/day (CI -$10.7 to +$32.1).
- Fewer than 20 test trades, so the locked word is UNDERPOWERED. Separate from power, size rules it out: taking 100% (not 10%) of the taker buying in the hour before the open, at the same per-share result, gives about $55/day on TEST and $100/day on TRAIN (exploratory arithmetic, not a locked metric). Median taker-buy notional in that hour, both tokens: $9.6k/day in TRAIN, $1.2k/day in TEST. Whole-event volume is now about $8-12k/day (12-18 Nov).

## What the data say
- The perp does price the open. sigma of (open - perp-implied open) = 15.5 bp (TRAIN); sign of the model is right 90.5% of TEST days, Brier 0.060 vs 0.25 for a coin. This repeats the 100/100 weekend result on weekdays.
- Polymarket already prices most of it. Mean |model p_up - Up ask| = 0.07. On days with a big perp move the book is at 0.00/0.99 and there is nothing to buy (e.g. 10 Nov, S = -77 bp).
- Own-token asks are sparse: a taker BUY print in the 5 minutes before T-30 exists on 19/74 TEST days for Up and 22/74 for Down.

## Controls (the test could fail and pass)
- Planted 5c edge: ex-ante edge reported 0.0500 on every row with an ask (30 TEST, 42 TRAIN); realised +0.072 TEST, +0.087 TRAIN, consistent with a calibrated model. Passed.
- Null plant (ask = model p): 0 trades in both halves. Passed.
- Sign-flip placebo: TRAIN +0.003 per share (CI -0.08 to +0.10); TEST +0.108 (CI -0.06 to +0.29, 14 longshot trades at mean ask 0.17). Not below 0 as the rule expected; with CIs spanning 0 this is the small sample, and it is a further reason the 7-trade TEST result means nothing either way.
- Yahoo open vs close sign agrees with Polymarket's resolution on 100% of non-tied days. Taker BUY prints on Up + Down sum to 1.008-1.013 on days with both, consistent with `side` being the taker's side.

## Unsupported / not done
- Only T-30 tested: the perp data are hourly candles. T-60 and T-10 need minute perp data.
- No live run today. Hyperliquid, Polymarket perps and Yahoo are blocked by this container's network; a live forward check needs `api.hyperliquid.xyz` allowed in the environment, or the PK arbs logger. Polymarket books are readable from here.
- Asks are trade prints, not book snapshots; depth beyond the prints is unknown. No historical order books exist publicly.
- Universe is SPX only. Other "Opens Up or Down" series (e.g. SPY, single stocks) were not enumerated; the SPY event on 18 Nov had $35 volume.
- Fee formula from mfw-clone T004 sources, not re-read from docs.polymarket.com (blocked).
