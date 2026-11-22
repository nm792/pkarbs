# REPLY 22 Nov 2026 ~07:00Z: R-036 item 2, perp-related arbs scan (INTERIM v1)

**1. Goal.** Strategies that reliably make $200/day before rebates and can be stacked (A9), sized under the capacity rule ($200 per trade, $2,000/day cap, measured own-token depth; print-sized numbers are FLOOR).
**2. Where it stands (measured).** No perp-related family has a MEASURED $/day. FLOORs: SPX/SPY "Opens Up or Down" +$5.3/day = 2.7% of $200 (CI includes zero; stale prints, scaled from the locked 10% slice; `weekend-perps/RESULT-open-contracts-2026-11-19.md`); weekly stock "hit" contracts after a weekend perp gap +$1.14/day = 0.57% (7 strikes, UNPROVEN; `weekend-perps/perp-scan-2026-11-22/run-2026-11-22/result_touch.json`). The perp signal is accurate: it had crossed the strike on 258 weekly strikes and YES won 217 (84%). Full ranked table of 9 families (daily $ volume, own-token ask depth, resolutions, $/day as % of $200, FLOOR or MEASURED): `weekend-perps/RESULT-perp-scan-2026-11-22.md`.
**3. The one item that matters most.** Decision-time depth of the weekly "hit" contracts. 8,264 of 8,575 strikes had no taker-buy print in the hour before the open, so a print test cannot see whether they can be bought in size before they reprice, and no historical book exists. Measurement: own-token book snapshots of all 58 events at Sun 22:40Z and 23:06Z (metals/oil reopen) and Mon 14:20Z (equity open), scheduled, plus IT row P92 (`ocbooks_depth.py` on the recorded SPX/SPY books). Final table by 23 Nov 12:00Z.

## Items
- Locked rule `weekend-perps/LOCKED-RULE-touch-gap-2026-11-22.md` (06:03Z), Amendments 1-3 before their numbers; tests and code `weekend-perps/perp-scan-2026-11-22/` (all can-fail tests pass); plausibility check and the disclosed n = 1 line are in the RESULT.
- IDEAS 4-10: capacity is not the limit (xyz books $40k-450k within 5 bp); verdicts stand as edge or cost verdicts; still open: IDEAS 8 rerun at 0.9 bp, IDEAS 10 at real book prices, IDEAS 5 forward check.
- Kalshi gold/WTI/silver/copper/S&P series: analysis only (A6), no $/day.
- OPEN-ITEMS row 7 updated (log); row stays OPEN.

Confidence 7/10. Below 9 because decision-time depth is unmeasured for every family, the touch FLOOR rests on 7 strikes, the stale-price figure is exploratory. To reach 9: the Sunday and Monday snapshots, IT P92 output, about 10 weekends of decision-time books.
