# SPEC (rule lock, pre-registered): weekend fade of after-hours gaps on the NVDA stock perp (OPEN-ITEMS 27, ledger L21)

Locked 25 Nov 2026 07:50Z by the Reviewer (was due 24 Nov 12:00Z in P-PERP-PLAN (B); slipped, owner silent). Paper/offline only. Nothing here may be changed after the data is read; any change is a new spec with a new date.
Known facts used: HL xyz taker fee 0.9 bp (SETTLED B.2, measured). Monte Carlo types follow Nick's G64 rule and are named in every result.

## Hypothesis and who pays
After the regular session ends on Friday, the NVDA perp on Hyperliquid xyz keeps trading while the stock does not. A price gap that opens in Friday after-hours, with no new information over the weekend, may be partly reversed by the Monday open. Who pays: weekend perp traders who chase the after-hours move against thin weekend books. Why it could persist: the stock market is closed, so cross-venue arbitrage is limited until Monday.

## Data (check first, before any return is computed)
- Perp: Hyperliquid xyz NVDA perp, 1-hour candles (public info endpoint) plus the 5 s book logger where it covers the weekend. Funding history for every hour held.
- Stock: NVDA official regular-session close (Fri 16:00 ET) and Monday open (09:30 ET), from a public daily source.
- Count the weekends where both exist. **If fewer than 13 weekends with a qualifying gap exist, the result is labelled UNDERPOWERED up front, not a fail.**

## Rule (primary, locked)
- R = NVDA official close Friday 16:00 ET.
- Entry time: Friday 20:00 ET (end of after-hours). G = perp mid at entry / R - 1.
- Trade only if |G| >= 1.0%. Direction: fade the gap (G > 0: sell the perp at its bid; G < 0: buy at its ask). Size $1,000 notional, capped by top-of-book depth where 5 s data exist.
- Exit: Monday 09:35 ET at the opposite touch (bid if long, ask if short).
- Cost: real touch prices where the 5 s logger exists; on candle-only weekends, the candle price plus half of the median observed spread from logged weekends, stated per row. Taker fee 0.9 bp each side. Funding paid or received over the hold, from HL funding history.
- Net return per trade in bp of notional. No pooling across symbols (NVDA only in this spec).

## Fixed secondary cells (reported, not used for the verdict)
Thresholds |G| >= 0.5% and >= 2.0%; exit Monday 16:00 ET.

## Tests that can fail
- **Planted case (MC type 2, randomised data, for power):** add a synthetic reversion of 30 bp toward R between entry and exit on every qualifying weekend; the code must recover a mean within +-5 bp of the plant. Also plant zero reversion; the code must not report a pass. Report the power to detect 30 bp at the actual sample size.
- **Placebo (MC type 1, random strategy on the same data):** 10,000 runs with the same entry/exit times, random sign, on every weekend regardless of G. The primary result must beat the placebo's 95th percentile.
- A delay check is not needed: entry and exit are hours apart and 1-hour candles are finer than the hold. (SETTLED B.1 is satisfied: resolution 1 h vs hold of ~61 h.)

## Verdict thresholds (locked)
- PASS: mean net > 0, bootstrap 95% lower bound over weekends > 0, and above the placebo 95th percentile, with >= 13 qualifying weekends.
- FAIL: these three met with >= 13 weekends and the mean net <= 0 with the upper bound < +10 bp.
- Otherwise INCONCLUSIVE, with the sample size and the power to see 30 bp stated.
Each report says: "we ran random-sign trades on the same weekends (MC type 1) to check the result, and planted 30 bp reversions in the data (MC type 2) to check the power."

## Delivery
Code `reviewer/pkarbs/perps/ah_gap_fade.py` + `test_ah_gap_fade.py` (planted pass, planted zero, placebo) by 25 Nov 12:00Z. Offline run in the container on public candles first (no Prime needed for 1 h candles); 5 s logger weekends via an IT read-only row after that.
