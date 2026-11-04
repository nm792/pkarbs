# CS2 event-only live pilot (capped)

Approved by Nick 4 Nov 2026 06:34Z. Rule and evidence: `winmodels/esports/bo3/NOTE-cs2-bo3-backtest-2026-11-04.md`
(PRs #44, #45, #47, #49).

| file | what |
|---|---|
| `pilot.py` | the bot (dry or live). Docstring has the rule, caps and log format |
| `model.py` | round model (pmap / series / betas from the backtest) |
| `test_pilot.py` | offline tests, synthetic books with hand-checked answers + replay of a logged match |
| `report.py` | summary of a run + the dry-run gates |
| `KEY-INSTALL.md` | how Nick installs the trading key on the server (never via chat) |
| `../../agent/tasks/cs2-pilot.md` | server task for the dry run |

## Rule as coded
- Markets: Match Winner + Map k Winner (map in play), events whose title names a tier-1 organiser (IEM, ESL Pro
  League, BLAST, PGL, Major, StarLadder, Thunderpick, FISSURE, EWC, Perfect World, CS Asia, Skyesports Masters) and
  volume >= $20k.
- Trigger: a within-map round score change on the Polymarket sports WS (1-3 rounds, map count unchanged).
  Map-end updates reach the WS 2-6 min late, so they are logged and skipped (the backtest did trade them, with true
  round times). This is the one deliberate difference from the backtest.
- Jump j = beta x model move (beta 0.570 maps, 0.558 match). If |j| >= 1c and the book mid has not moved by j since
  30 s before the event: for 30 s rest a post-only BUY on the rising side at mid x 0.975, floored to the tick.
  Cancel when the move shows up, the mid leaves 5-95c, the window ends, or the fair - bid < 1c (Nick's E rule).
  Re-quote when the target price changes by a tick. Hold to result.
- Mid = live order-book mid (backtest used a trade-derived mid). Book polled every 1 s.

## Caps
- $250 per match (filled cost + open orders), 1,000 shares per order.
- Total: open exposure <= $500 + min(realized P&L, 0), so total loss can never pass $500; at -$500 realized the
  pilot halts (cancels all) and only tracks resolutions. State persists in `OUT/state.json`.
- Live safety: post-only orders only; order heartbeat every 5 s (Polymarket cancels our orders if the process stops);
  cancel-all at start, stop and halt; `OUT/STOP` kill file; live mode refuses to start unless the region check passes,
  the key file is mode 600 and a person has written `OUT/LIVE_OK`.

## What the logs answer
- queue: size resting at our price when we join, and how it shrinks (`queue` rows), vs fills.
- fills: real fills (live) and paper fills from public prints, naive (first in line) and queue-adjusted.
- markout: token mid 60 s after each fill.
- feed delay: WS receipt time minus the time the book mid made half its move (-60..+60 s around the event).
