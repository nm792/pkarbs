# Addendum to the mentions forward test (10 Nov 2026, before any forward event is scored)

The Polymarket audit (PR 254) found the 3c rule fails on Polymarket and only 10c passes. The forward test now has two arms:

- Kalshi arm: unchanged, 3c, mentions/mm_forward.py.
- Polymarket arm: 10c is the PRIMARY (and only decision) variant; 3c and 5c are printed for information only. Scorer: mentions/pm_forward.py. Same freeze time (events started at or after 2026-11-10T15:00:00Z), same per-word base rate (alpha 2, family history = all earlier closed events), first-hour BUY prints priced 5c to 95c, hold to resolution, one bet per event, print size.

Decision rule per arm (single test, no variant correction): after 100 or more forward events with at least one bet: PASS if net P&L > 0 (Kalshi after taker fees), paired t vs same-event placebo >= 2, log score vs market first print > 0, top 3 bets under 50% of P&L, cluster t > 1.5. FAIL if net <= 0 after 100 events, or log score < 0 with paired t < 1. Otherwise unknown, continue to 200 events. Rule is not changed on the forward sample.

## lockstat fix
lockstat.placebo_same_event scaled each random same-event print by min(fill size, bet size). That shrinks the placebo whenever prints are smaller than the bet and flatters the result. It now uses the bet's own size. Effect on the existing results: Kalshi pooled 3c paired t 3.75 to 3.03 (Bonferroni x3 0.01); Kalshi held-out half 2.18 to 2.17 (Bonferroni 0.09); NBA series alone 4.12 to 1.85; Polymarket 3c all t 2.26 (Bonf 0.07), held-out 2.06 (Bonf 0.12); 10c all t 4.61, held-out 3.53.

## Order books
Mentions order-book snapshots at market creation, for new mention markets on both venues, are requested separately from Hermes through the repo.
