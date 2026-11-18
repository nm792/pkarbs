# Reviewer: the perp-priced Polymarket open contract was never tested (18 Nov 2026)

For the PK arbs project's Claude. Reply in `reviewer/REPLY-2026-11-18-perp-open-contracts.md`, opening per REPLY-RULES.md and citing SETTLED.md.

## Goal-level assessment
- **Goal:** strategies that reliably make $200/day before rebates and can be stacked (SETTLED A9).
- **Where it stands:** your backfill shows the weekend perp calls the cash open 100/100 (`weekend-perps/REPORT-backfill-2026-11-16.md`, slope 1.006, CI 0.94-1.07). Your own rule said the trade is in the lagging instrument (`weekend-perps/LOCKED-RULE.md:40`). Polymarket lists "S&P 500 (SPX) Opens Up or Down on <day>" (about $6.1k/day, 42 events in 60 days, `scan/OUT-pm-tradfi-2026-11-11.md:9`). Those markets were never compared with the perp.
- **The one item that matters most:** run that comparison. Nick, 18 Nov 08:31Z, raised it directly.

## Finding
Step 2 was run against Polymarket perps only (REPORT-backfill line 25: "Polymarket perps are within a median 2.8 bp of Hyperliquid, so Polymarket is not lagging"), then marked untested. The open contracts named in your own rule were not used. The tradfi scan tested an early-leader rule on the same series, not the perp signal. It also priced the ask as mid + 1.5c, not from the token's own book (SETTLED A1). This is an untested, dropped idea (IDEAS.md row 0).

## Required test (locked before any number, and able to pass)
1. Universe: every resolved Polymarket open contract on US cash indices and single stocks (Opens Up or Down, open above strike, if listed), Aug 2026 to now. Include weekday opens as well as Mondays: the perp leads every open.
2. At fixed checkpoints (T-60, T-30, T-10 min before the cash open), compute the perp-implied P(open > strike) from the perp mark relative to the strike. Use the residual sd of O - S measured on the training half only.
3. Price each side from **its own token's ask** at that checkpoint, using logged or historical book data. If no own-token book exists for a row, exclude and count it, never mirror (SETTLED A1, B2). Use Polymarket fees from the docs.
4. Edge = model probability - own ask - fee. Trade when edge > threshold (fix it in advance). Hold to resolution. Report hit rate vs ask, edge per contract, depth at the ask (shares and $), $/day at a 10% slice of depth, an event-clustered CI, a sign-flip placebo, and the train/test split by date.
5. Planted check: on a copy of the data, shift asks to make a known 5c edge. The code must find it, and it must return about 0 on asks set to the model probability.
6. Verdict against $200/day on the CI lower bound, before rebates; rebates reported separately. Also report correlation with other candidates and the capital it ties up.

Deadline: 19 Nov 08:00Z for the locked rule and the result. Analysis only, no orders.
