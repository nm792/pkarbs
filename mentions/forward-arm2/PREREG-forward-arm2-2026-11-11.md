# Mentions forward test, ARM 2: pre-registration (frozen 11 Nov 2026, events opened at or after 10:00Z)

Status: paper only. No live orders. This note and `mm_forward2.py` are merged BEFORE any arm-2 event is scored, and before the freeze time. Arm 1 (PREREG-forward-test-2026-11-10.md, 10 series, scorer `mm_forward.py`) is untouched and keeps its own decision.

## Why
Arm 1 has seen 2 events in 18 hours (none resolved), which would take months to reach 100. Arm 2 applies the identical rule to every other Kalshi mention series.

## Rule (identical to arm 1, no tuning)
- Venue/series: Kalshi, category Mentions (465 series on 11 Nov), excluding the 10 arm-1 series (KXVANCEMENTION, KXNFLMENTION, KXNBAMENTION, KXWCMENTION, KXMAMDANIMENTION, KXBERNIEMENTION, KXSECPRESSMENTION, KXTRUMPMENTIONB, KXTRUMPSAY, KXTRUMPMENTION). No double counting between arms.
- Model: online per-word base rate within the series, q = (wins + 2*gp) / (n + 2), gp = series-wide base rate, using only events whose markets had ALL settled before this event opened (settlement time = the earlier of close_time and settlement_ts; the causal rule from the 10 Nov audit).
- Entry: first taker BUY print in the first hour after the event opened (earliest `open_time` of its markets): YES print buys YES at the yes price, NO print buys NO at the no price; price 5c to 95c; edge >= 3c (YES: q-p; NO: (1-q)-p); one bet per event; size = the print size; hold to resolution. 3c ONLY.
- Eligibility, decided mechanically per event (no hand-picked list): the event has at least 3 markets, all resolved yes/no, opened at or after the freeze, and its series has at least 10 earlier resolved events (each at least 3 markets) that had settled before this event opened. The list in `eligible_snapshot_2026-11-11T0900Z.json` (16 series, 61 events in the prior 30 days) is informational only; series enter arm 2 automatically when they reach 10 resolved events.
- Forward sample: events opened at or after 2026-11-11T10:00Z (constant `FREEZE` in `mm_forward2.py`).
- Fees: Kalshi taker fee ceil(0.07*C*P*(1-P)), net P&L reported after fees.

## Decision (single test, no variant correction, per arm)
After 100 or more forward events with at least one bet:
- PASS: net P&L after fees > 0, paired t of real vs same-side same-event placebo at the bet's own size >= 2, log score vs market first print > 0, top 3 bets under 50% of P&L, cluster (week) t > 1.5.
- FAIL: net P&L <= 0 after 100 events, or log score < 0 with paired t < 1.
- Otherwise unknown, continue to 200 events. The rule, thresholds, eligibility and series set are not changed on the forward sample. Reported for information only (not decision): per-series results, results with bets capped at 25 contracts, and arm 1 + arm 2 pooled.

## Expected volume
Measured on 11 Nov 09:00Z from the Kalshi API (counts only, no performance looked at):
- 16 eligible series today (at least 10 resolved events, an event in the last 30 days, excluding arm 1); they opened 61 events in the last 30 days and 175 in the last 90 days, i.e. 13.6-14.2 events per week. KXWORLDNEWSMENTION alone is about a third of that (22 in 30 days); the top 3 series are about 60%.
- Counts-only dry run of the scorer with a test freeze of 12 Oct: 243 events opened, 112 unresolved at the time of the run, 55 eligible and resolved, in 13 series (about 13 per week).
- Not every event produces a bet: in the earlier Kalshi backtest about 80% of events had a qualifying print (592 of 744); assume 50-80% for these series.
- Date to reach 100 events with a bet: 100 / 0.8 = 125 events, about 9 weeks, around 14 January 2027; at 50% it needs 200 events, about 14-15 weeks, around 25 February 2027. Central estimate (65%, about 155 events, 11 weeks): about 28 January 2027. The count grows as more series reach 10 resolved events, which shortens these dates, and falls in holiday weeks (late December).
- Resolution lag (events must settle before scoring) adds a few days.

## Limits
Only 16 of 165 recently active non-arm-1 series qualify today; 149 have fewer than 10 resolved events (mostly one-series-per-company earnings calls). A per-word base rate on a pooled earnings-call family would use these but is a different model and needs its own pre-registration.
Everything here is paper. The first arm-1 entries (Vance/Trump 11 Nov) are scored separately when they resolve.
