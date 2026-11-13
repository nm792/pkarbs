# Mentions forward test: pre-registration (frozen 10 Nov 2026 15:00Z)

Status: paper only. No live orders. This note is merged BEFORE any forward event is scored.

## Rule (frozen, no tuning)
- Series: Kalshi KXVANCEMENTION, KXNFLMENTION, KXNBAMENTION, KXWCMENTION, KXMAMDANIMENTION, KXBERNIEMENTION, KXSECPRESSMENTION, KXTRUMPMENTIONB, KXTRUMPSAY, KXTRUMPMENTION; Polymarket tag mention-markets (families: trump-event, trump-weekly, earnings-call, sports-announcers, other).
- Model: online per-word base rate q = (wins + 2*gp) / (n + 2), gp = family-wide base rate, using only earlier settled events.
- Entry: first BUY print in the first hour after the event opened (Kalshi open_time; Polymarket earliest market startDate), price 5c to 95c, edge >= 3c (YES: q-p; NO: (1-q)-p). One bet per event, size = the print size, hold to resolution.
- 3c ONLY. 5c and 10c are not part of the forward test.
- Forward sample: events whose open time is at or after 2026-11-10T15:00:00Z.
- Code: mentions/mm_forward.py (Kalshi, same run() as mm_all.py with freeze time); Polymarket equivalent pm_mm_bt.py logic with the same parameters.

## Decision (single test, no variant correction)
After 100 or more forward events with at least one bet (Kalshi and Polymarket pooled, stats also reported per venue):
- PASS: net P&L after Kalshi taker fees > 0, paired t of real vs same-event placebo >= 2, log score vs market first print > 0, top 3 bets under 50% of P&L, and cluster t > 1.5.
- FAIL: net P&L <= 0 after 100 events, or log score < 0 with paired t < 1.
- Otherwise: unknown, continue to 200 events. The rule is not changed on the forward sample.

## Baseline context (not part of the test)
- Kalshi pooled, 9 series, 3c: +$2,624 on $25,341 gross (+$2,372 net of fees), paired t 3.75, log score +0.050. Held-out half +$906 net.
- Polymarket, 909 events, 3c: +$1,732 on $3,898, held-out paired t 2.58, log score +0.125.
- Kalshi events since 15 Sep 2026: +$156 on $490, log score -0.029 (edge may be fading; this is why the forward test exists).

Any improved word-level model is a separate candidate with its own pre-registration; this note stays as the baseline.
