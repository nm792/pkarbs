# RESULT: perp vs Polymarket "SPY Up or Down on <date>" (Reviewer prototype, 19 Nov 2026)

Rule `LOCKED-RULE.md` committed 803825d7 before scoring. Code `score.py`; inputs `data/` (Polymarket gamma + data-api v2 trades pulled 19 Nov 02:23-02:36Z by `fetch_pm.py`; Hyperliquid xyz:SP500 1 h candles and ^GSPC Yahoo daily bars from pkarbs main d9f9f905 `weekend-perps/backfill-2026-11-16/data/`). Outputs `result.json`, `trades_test.json`, `reconcile.tsv`. Rerun: `python3 -I score.py`.

## Verdict (locked): FAIL
TEST, 1 Aug - 13 Nov (74 days, 1,702 hourly checkpoints, 148 trades on 59 days):
- Realised per share +0.025 (CI -0.063 to +0.125, clustered by day). Hit 34% at mean ask 0.31; ex-ante edge 0.076.
- **$68/day (CI -$9 to +$190)** at 10% of the taker flow. Tradeable notional at that 10%: **$55/day**. Rebates $0.34/day.
- The sign-flip placebo makes the same money: +$64/day, +0.027 per share. The profit is a few cheap longshots paying out, not the perp signal.
- Session checkpoints (last 6 h): +0.079 per share (CI -0.02 to +0.19), $69/day. Overnight: -0.031 per share, -$1/day.
- TRAIN (22 Apr - 31 Jul, 69 days): 243 trades, +0.050 per share (CI -0.036 to +0.131), $39/day (CI -$101 to +$157); tradeable $469/day. Placebo -$72/day.

## What the data say
- The perp is a good forecast late in the day and a weak one overnight. Sign hit on TEST: 89.6% in the last 6 h (Brier 0.092), 61.5% overnight (Brier 0.218). sigma of close vs perp: 28 bp at 1 h to the close, 54 bp at 6 h, 82 bp at 23 h (TRAIN).
- Polymarket is already close to it: mean |model p_up - Up ask| is 0.077 in the session and 0.041 overnight (TEST).
- Size: USD traded per event, all trades: May $74k, Jul $43k, Aug $19k, Sep $16k, Oct $9k, Nov (to 18th) $8k. Gamma `volume` is shares: pulled shares equal gamma volume to 4 dp on 139/148 events (the 20-29 Apr ones are 95-99%). At 10% of the hour's taker buying, tradeable flow on TEST is $55/day; all of it is about $550/day of notional.

## Controls
- Planted 5c edge: ex-ante 0.0500 on all 485 TEST checkpoints with an ask; realised +0.079 (CI +0.033 to +0.122). Found. TRAIN +0.065.
- Null plant (ask = model p): 0 trades in both halves.
- Placebo: TRAIN -0.025 per share (expected sign); TEST +0.027 (not below 0, so the TEST primary has no signal beyond chance).
- Yahoo ^GSPC close-to-close sign agrees with Polymarket's SPY resolution on 97.3% of TEST days (SPX vs SPY; dividend days and near-zero days differ). Payouts use Polymarket's resolution.
- No lookahead: perp = close of the 1 h candle ending at the checkpoint; ask = last taker BUY print in the 5 minutes up to the checkpoint.

## Live read, 19 Nov 02:22Z (`LIVE-READ-2026-11-19.json`)
Own books, 19 Nov event: Up best ask 0.72 x 500 (top 5 asks $1,586), best bid 0.69; Down best ask 0.31 x 106 (top 5 asks $913), best bid 0.28. Perp NOT read: api.hyperliquid.xyz is blocked from this container, so no live model probability or edge.

## Unsupported / not done
- Hourly checkpoints only (hourly candles). Minute-level perp data would allow the 250 ms / seconds-scale entry question; this test says nothing about it (SETTLED B1).
- Asks are taker prints, not book snapshots; no public historical books.
- The live perp read needs api.hyperliquid.xyz allowed in this environment's network settings, or the PK arbs logger.
- Fee formula from mfw-clone T004 sources (docs.polymarket.com blocked).
