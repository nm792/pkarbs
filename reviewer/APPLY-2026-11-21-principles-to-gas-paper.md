# Applying MODELLING-PRINCIPLES.md to the gas paper run (Nick 21 Nov 06:51Z: standing method for PK arbs)

Goal: rules that can each reliably deliver $200/day (SETTLED A9), ranked and stacked. Position: gas daily best case $11.74/day at an upper-bound fill model (15c43a29); paper run cleared for `post` 20 Nov (R-002), not started (R-003). Top item: capacity first (s.14). Gas is already **capacity-limited**: keep it as a stacking candidate, but measure depth before any edge claim.

This note replaces the R-002 acceptance rule ("20 events, post net > 0, >= 95% hits"). The R-002 conditions on page log, decision-time books and settlement still apply.

1. **No hindsight (s.8).** `post` decides from the AAA value in the logged page read at the decision time, never from the settlement value. A decision with no page read logged before it is void. The backtest's 100% hit came from using the settlement value (R-002 item 2).
2. **Score against later prices as well as settlement (s.12).** For each decision, log the token's own best ask and bid at +1 min, +5 min, +30 min and 10:00 ET, and score markout at each horizon as well as settlement P&L.
3. **Estimate and shrink, not pass/fail (s.5, s.6).** Log `post`, `yes_fav` and `no_out` as ranked cells. Each gets a shrunk estimate of edge per $ with an interval. `yes_fav` v2's three-day result is shrunk, not deleted.
4. **Positive control and power before any verdict (s.2).** Before day 1, run a planted cell: a replayed day with a known stale ask must show up as a positive markout through the same code. Also state how many events are needed to see the backtest edge (+37c per $ in the reviewer prototype, 38af8276; your per-fill variance) at the planned size. No verdict is allowed before that count.
5. **Sequential stop rules (s.13).** Register for each cell: score, success boundary (always-valid lower bound above cost), futility boundary (always-valid upper bound below cost), and a maximum sample after which the cell is reported as "inconclusive, ranked". Look at it any day; stop only at a boundary.
6. **Capacity first (s.14).** For each cell, give median and 10th-percentile own-token ask depth at or better than the decision price (from decision-time books), fills/day, $ edge/day at that depth, and the share of $200/day. Rebates are reported separately (A9).

Reply in INBOX with the registered boundaries, the power count and the positive-control result, each with a commit.
