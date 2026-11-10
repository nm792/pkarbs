# Box office: correction after the independent audit (10 Nov 2026)

The earlier note (NOTE-box-office-later-weekends-2026-11-10.md) said "first pass". That is withdrawn. Status: **unknown, settled by forward test.**

Why: the z of 4 to 6 divided by the placebo's spread, not the real P&L's spread. Recomputed with lockstat.py (paired real minus same-event placebo, per-event spread): 6h/5c t=2.7 (Bonferroni over 4 variants p=0.03), 2h variants t 1.3 to 1.9 (p 0.10 to 0.18). Weekend-clustered t 1.6 to 2.4. Top 3 bets are 60 to 85% of P&L (6h/5c: $101 of $168; 2h: $71 of $85). The independent audit (audit-box-office-2026-11-10) finds the real result is only 0.6 SD above an all-events random print and that the model's log score is worse than the market's first-print probabilities on 14 events. Total size about $100 to $200 over two years.

New standard for every test from now on: forecast-edges/mrbeast-style/lockstat.py, which prints real-vs-same-event-placebo paired t, cluster t, top-3 concentration, variant-count correction, and an optional log score against market first-print probabilities. Nothing is called a pass unless the paired t survives the variant correction in the held-out half, concentration is not top-3 driven, and the log score is not worse than the market.
