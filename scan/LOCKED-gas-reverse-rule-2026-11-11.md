# LOCKED RULE (written 11 Nov 2026 before any new data was looked at)
Origin: momentum test (scan/OUT-gas-signal-cheap-2026-11-11.md) found the last-AAA-change direction came true 23-40% in CA/NY vs ~45% implied.
This is a hypothesis from that data, so it is tested ONLY on data the momentum test did not touch.

**Rule (reverse / mean-reversion):** on Kalshi state daily AAA gas (KXAAAGASD<ST>), for strikes within 3c of the prior-day AAA value whose YES mid is 25-75c one hour after open,
bet AGAINST the direction of AAA's last daily change (prior day minus the day before): if it rose buy NO, if it fell buy YES. Skip days with zero change.
Fill at the ask (YES) or 1 - bid (NO), Kalshi fee 0.07 p(1-p), hold to settlement.

**Test data:** state series NOT used in the momentum test: all states except CA, TX, FL, NY (up to 8 with data), the 30 most recent events each. No CA/TX/FL/NY.
**One test, no variants.** Pooled over the fresh states, event-clustered bootstrap CI on the gap (win rate - ask - fee), plus sign-flip placebo (2000 draws).
**PASS only if:** pooled gap > 0 with 95% lower bound > 0, hit rate above market-implied, placebo z >= 2.0, and at least 100 strikes from at least 40 events.
Anything else = FAIL / unproven (no re-picking the rule, band, or horizon on this data).

**State list (fixed by event count, before running):** IL, NJ, WA, NC, OH, PA, GA, VA.
