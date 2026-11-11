# Netflix test audit and data plan (10 Nov 2026, 08:30Z)
Measured = computed. Files in forecast-edges/mrbeast-style/ (audit.py, nf_full.py, *_v2_placebo.txt, mb_bt2.py, pers_bt2.py).

## Bug found: the "matched placebo" could not detect a perfect model
Test: replace the model probability with the true outcome (oracle, must win big) and with its opposite (must lose).
- Sign and side logic are CORRECT: oracle wins 43 of 43 bets, anti-oracle loses 42 of 42.
- The placebo (v1: same side, price within 5c, drawn from the same event's window) was broken: even the oracle only beat it by +0.4 sd, because it mostly re-drew the bet itself or its twins. So "cannot beat random picks matched on side and price" was meaningless as stated.
- v2 placebo: same side and price within 5c, drawn from OTHER events' prints in the same selection. It detects the oracle (+5.8 sd test, +7.5 sd all) and the anti-oracle (-29 sd).
Everything earlier that used the matched same-window placebo (Netflix full model) is superseded; MrBeast and persistence were rerun with v2.

## Results with the fixed placebo (held-out half)
- Netflix global, full model, primary (5c, 2h, T=start+1h): 14 bets, +$63 vs placebo +$36 ± 21 = +1.3 sd; first half -1.7 sd; whole sample -1.1 sd. Threshold 3c/10c: +1.5/+1.0 sd. With T = close-72h: -2.5 to -2.9 sd in every threshold. 6h window with T=start: +3.8 sd but it is ONE $5,190 fill carrying $5,379 of $5,379 pnl, i.e. one event, not evidence. Verdict: NOT a pass (inconsistent across decision times, 14 bets).
- MrBeast day-N: test -3.5 sd (M2 continuation -4.2 sd). No edge, if anything worse than random.
- Rank persistence, all families: test -1.1 sd (first half +21 sd is in-sample, the rule's rate was fitted on it).
- Calibration check, Netflix global candidates (121 candidate-events): model Brier 0.2143 vs market first print 0.2088. The model is slightly WORSE than the market. Expected: last week's official hours are public and priced; the winner was not on last week's top-10 list in about half of events (new releases), which this model cannot see.

## Why the model sits near random
It only uses last week's official hours. The market already has that, plus this week's daily lists. The information that moves the answer inside the week is not in the model: daily/hourly rankings for the current week and early signals for new releases.

## Cheapest legitimate source of intra-week data
- FlixPatrol API: paid, $49/month or $490/year (daily top 10 by country, historical dates; their changelog says all history is available). The site bot-blocks our fetches, and I will not use a stealth browser to get round that. This needs Nick to buy it (or approve me to).
- Free pages on FlixPatrol and What's on Netflix (daily top 10) exist but bot-block or have no history; archive.org holds only 2021 FlixPatrol snapshots, nothing from 2026.
- Hermes recording from the server: only worthwhile for a source that permits it; not started.
Without history, a recorder needs about 8-10 weeks to produce a first held-out half, so history from the API is the difference between hours and months.
Confidence 8/10 on the bug and its fix (oracle test is direct); 7/10 on "no pass".
