# Lag test v2 result: perp vs Polymarket SPY Up or Down, all events 3 Aug - 20 Nov 2026 (Reviewer, 23 Nov)

Rule `LAG-RULE-v2.md` (ed61a208, before data). Code `fetch_perp_1s.py`, `lag_v2.py`. Output `lag_v2_result.json` (incl. per-event rows). Inputs: Polymarket perps SP500-USD 1 s marks (`data/perp1s/`, 79 events, ~87k marks each), data-api v2 prints (`data/trades_*`), TRAIN sigma/mu from `result.json`. C0 check: perp at prior close vs Yahoo ^GSPC prior close, median 3.2 bp, p90 9.8 bp (74 events).

## Answer
**Polymarket does lag the perp, but buying the prints the perp says are stale did not make money.**

## Lag (moves of >= 10 bp in 60 s; 620 moves, 393 with a Polymarket price just before)
- Time until a print covers half the perp-implied probability jump: p25 61 s, **median 253 s**, 109 of 393 (28%) not caught up in 30 min. 52 within 10 s, 98 within 60 s, 206 (52%) within 5 min.
- Big moves (|dp| >= 0.05): median 141 s, 63% within 5 min. Smaller (|dp| < 0.05): median 642 s, 39%.
- Much of it is waiting for any trade: median time to the next print of any kind is 92 s.
- Controls: planted 30 s reaction measured as 30 s on 388 of 393 (the other 5 had a real print catch up first). Random no-move times: 16% "caught up" within 5 min vs 52% after real moves. The lag is real, not print noise.

## Stale prints (taker buys more than fee + 1c below the perp fair value)
- 11,251 prints, **$215,554 of $923,498 taker buying (23%)**, $2.7k per event.
- Realised at resolution: **-$20,285** (per-event CI -$68k to +$36k). Placebo with a perp 30 minutes old: -$28,922 (CI -$73k to +$20k). The live perp is slightly better than a stale one but neither is positive.
- By month (taker-buy $/event; stale $/event; stale P&L/event): Aug 17,201 / 3,201 / -579; Sep 12,942 / 2,840 / -56; Oct 8,209 / 1,631 / -188; Nov 7,326 / 3,520 / -188.
- Reading: "cheap against the model" prints lose because the model's error (unconditional sigma, SPX vs SPY) is larger than the gaps it finds, not because the perp is wrong about direction.

## What this does not answer
- Quote lag. Prints only show when someone traded. The book may reprice within seconds of the perp. Live book logger started 23 Nov ~14:00Z (`book_logger.py`, `live_2026-11-23_book.jsonl`, perp + both books every 2 s) to measure that directly.
- A trade rule that buys the ask right after a move. No historical books exist; the live logger is the only way.
