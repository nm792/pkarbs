# LOCKED RULE: Edgeworth price-cycle drift in OH, MI, IN (WI if listed) (written 11 Nov before testing)
Hypothesis: after a sharp retail jump the price drifts down for days until the next jump.
Qualifying day D (state series KXAAAGASD<ST>): an AAA state jump of +5c or more (day over day) occurred within the previous 10 days, AND the last daily change (D-1 minus D-2) is below +5c (D-1 was not itself a jump), AND D itself is not known to be a jump (not knowable in advance, so none of this uses D's value).
Trade: strikes with floor_strike >= the prior-day AAA value and within 3c of it, whose YES mid is 25-75c one hour after open: buy NO (price will not exceed the strike) at 1 - bid, Kalshi fee 0.07 p(1-p), hold to settlement.
Data: all consecutive-day history available for OH, MI, IN and WI (if listed). One test, no variants (no re-picking jump size, window, strike side).
Held-out: first half of dates = train, second half = TEST (headline); event-clustered 95% CI on gap (win rate - ask - fee); placebo = same strikes with the side flipped at random per event, 2000 draws.
Size: 10% of $ traded in the 2 hours after hour 1 (x0.5 taker-buy share); $/day = sum(size x return) / calendar days of the sample.
PASS only if TEST gap > 0 with CI lower bound > 0, placebo z >= 2.0, hit rate above market-implied, and >= 100 TEST strikes from >= 40 events. Fewer = UNPROVEN (counts reported).
