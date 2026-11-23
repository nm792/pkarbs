# Catch-up trade result, historical (Reviewer, 23 Nov 2026)
Rule `CATCHUP-RULE.md` (2049e5a5, before data). Code `catchup.py`. Output `catchup_result.json` (all trades, grid, splits, 15 examples). Inputs as `LAG-RESULT-v2.md` (79 events, 3 Aug - 20 Nov).

## Verdict: UNDERPOWERED. No "no edge" call is allowed: the planted 3c edge is not detected.
- Primary (enter within 60 s of the move at the first real ask fill of the stale token, exit at the first real bid fill after catch-up or a 15-min stop): **38 trades on 27 of 79 events**, mean **-2.9c per share (CI -6.9c to +1.0c)**, hit 50%, -$0.06/day at 5 shares.
- Planted +3c on every trade: CI -3.9c to +4.0c. This sample cannot tell a 3c edge from zero, so the prints cannot settle the question.
- Why so few: a stale-token buy print inside 60 s of a 10 bp move exists for only 38 of 393 measurable moves. Exits wait for a sell print: median hold 22 min.
- Grid (N entry window / S stop): N30 S300 +0.5c (26 trades), N30 S900 -1.3c, N60 S300 -1.7c, N120 S300 -2.1c (56), N120 S900 -3.0c (CI -6.4c to +0.1c). All CIs span 0.
- Splits (primary): moves 10-20 bp -3.5c (34 trades), > 20 bp +2.6c (4). US session -5.1c (27; CI -9.4c to -0.9c), outside session +2.4c (11). Entry delay <= 10 s -1.3c (14), 10-30 s -1.3c (12), 30-60 s -6.3c (12).
- Null control (random times, no move): 17 trades, -4.2c, hit 24%. The real moves do better than random, but not significantly.

## Next
Historical prints cannot test the trade at the ask. The live loggers (`book_logger.py` 2 s; `book_logger_v2.py` 1 s with the perp's own bid/ask) record both SPY books through today's US open. The live version of this rule is scored on them when they end (~16:00Z).
