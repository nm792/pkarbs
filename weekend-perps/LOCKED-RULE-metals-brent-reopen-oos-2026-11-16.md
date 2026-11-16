# LOCKED RULE: metals fade / Brent follow around the Sunday futures reopen, out-of-sample test (16 Nov 2026, written before any number of this test was computed)

Origin: the post-hoc variant in RESULT-pm-drift-and-commodity-fx-2026-11-16.md found that after the weekend move of the perp, the reopen falls back for silver, copper and platinum (D -56 to -104 bp) and extends for Brent (+48 bp). That was found on 30 weekends (22 Apr - 16 Nov 2026, 1 h candles) with 7 symbols looked at. Nick's rule: test it out of sample, with realistic costs and capacity. Only these four are tested; gold, CL, natgas and palladium are NOT part of the hypothesis.

## Hypotheses (fixed)
H-metals: for xyz SILVER, COPPER, PLATINUM, after a weekend perp move of >= 50 bp, the position AGAINST the move earns more than costs. H-brent: for xyz BRENTOIL the position WITH the move earns more than costs.
## Data
Hyperliquid xyz perp candles; Yahoo 1 h futures bars as the weekend-reopen reference (gap > 36 h between consecutive bars; F = last bar close before the gap; T = first bar start after it). Perp Friday close Pf = perp close of the candle ending at or before the end of the last reference bar. Signal Sown = (P_entry / Pf - 1) in bp, where P_entry = close of the last perp candle ending at or before T-30 min. Signal if |Sown| >= 50 bp.
## Samples
- Discovery (already seen, reported only for reference): T on or after 22 Apr 2026, 1 h candles.
- Coarse replication of discovery: the same weekends rebuilt with 4 h candles (checks that 4 h resolution does not change the answer).
- HELD-OUT (the test): weekends with T before 22 Apr 2026, back to the start of each perp's 4 h history (gold/silver Dec 2025, copper Jan 2026, platinum Jan 2026, Brent Mar 2026), 4 h candles. Not looked at before this rule.
## Trade
Position: fade (metals) = -sign(Sown); follow (Brent) = +sign(Sown). Entry price = P_entry. Exit price = close of the first perp candle whose END is at or after T + 60 min. Gross = position x (exit / entry - 1) in bp.
## Costs (conservative, set before computing)
Taker fee 9 bp per side (Hyperliquid base 4.5 bp, doubled for HIP-3 builder markets; the actual xyz rate is not published in the API, 4.5 bp is shown as a sensitivity only). Half-spread per side = max(3 x live half-spread, 1 bp), with the live spread taken from the l2Book at 16 Nov ~15:30Z (a stress multiplier because weekend books are thinner than a Monday-afternoon book): about 1.0 bp for silver/Brent, 4.9 bp copper, 6.2 bp platinum. Funding over the holding period is ignored (hold ~1.5 h). Net = gross - 2 x (fee + half-spread).
## Capacity (reported, not a pass criterion)
From the live l2Book: notional fillable within 5 bp of mid on the entry side, and as a share of open interest; per-trade size where impact is 5 bp; weekly signal count per symbol. Capacity per weekend = signals per weekend x that size, stated as an upper bound.
## Decision rule (applied to the HELD-OUT sample only)
H-metals PASSES only if, pooled across the three metals, n >= 15 held-out signals over >= 8 weekends AND mean net > 0 with the weekend-cluster bootstrap 95% CI (10,000 resamples, seed 1) lower bound > 0 AND gross mean has the hypothesised sign in >= 2/3 of the weekends with a signal AND no weekend contributes more than 40% of total net. H-brent is judged the same way but with n >= 8 signals; if the held-out sample is smaller than that the answer is "unknown" and the weekends needed are stated. FAIL if the held-out gross mean has the wrong sign or the net CI upper bound is below 0. Anything else is "unknown (too few weekends)".
A pass is not an edge claim: it justifies a forward test on the live logger from 21-23 Nov, once the logger records the metals and Brent books (separate IT task). No parameter above may change after the first number is seen; any new idea needs a new rule file.
