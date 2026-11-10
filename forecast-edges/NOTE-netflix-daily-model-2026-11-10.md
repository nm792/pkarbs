# Netflix with free daily lists (10 Nov 2026, 09:00Z)
Measured = computed. No orders. Scripts/outputs in forecast-edges/mrbeast-style/ (nf_daily.py, nf_daily_output_strict.txt, wn_daily_160days.json.gz).

## Free data found (no purchase)
What's on Netflix publishes the daily Netflix top 10 for 12 countries (US, UK, AU, BR, CA, FR, DE, IN, MX, NL, NZ, ES) and a global top 50 with points, for any past date (`/most-popular/?dateselect=MM/DD/YYYY`; robots.txt allows it; one request per page). I pulled 160 days: the Monday to Wednesday of every market week (Mar 2025 to Nov 2026). US and 12-country lists exist for 158 of 160 days; the global points chart only for 93 (missing Oct 2025 to Jan 2026), so the model uses only the country top-10s.

## Model
Per candidate title: average over the week's days so far of (11 - rank) in the US list, and of the 12-country sum. Conditional logit over the event's matched candidates (grid-fitted on the first half of events, rank-2 by Plackett-Luce), mass scaled to the market's own total on matched titles so unmatched titles carry no bias. Strict availability: a day's list counts only if the whole day is over before the decision time (T = market start + 1h, usually Wednesday or Thursday). My first run allowed Tuesday's list when some markets opened earlier on Tuesday night; that was a possible leak, I fixed it before reporting.

## Locked test (first qualifying print, full print size, placebo matched on side and price from other events, events as units, split by time, every variant in nf_daily_output_strict.txt)
Primary, 5c threshold, 2h window, per-event units; bootstrap 95% CI of mean P&L per event (zero for no-bet events):
| | events | bets | P&L | v2 placebo | per-event mean, CI |
|---|---|---|---|---|---|
| US all | 88 | 28 | +$150 on $387 | +$8 ± 29 | $1.71 [0.07, 3.81] |
| US first half | 55 | 17 | +$128 | | $2.33 [-0.08, 5.65] |
| US test half | 33 | 11 | +$22 on $148 | -$18 ± 15 | $0.67 [-0.69, 2.09] |
| Global all | 95 | 39 | +$93 on $553 | +$25 ± 35 | $0.98 [-0.77, 2.72] |
| Global first half | 57 | 23 | -$25 | -$26 ± 28 | -$0.43 [-2.92, 2.03] |
| Global test half | 38 | 16 | +$117 on $280 | +$52 ± 25 | $3.09 [1.42, 4.95] |
Nearly all bets are buying NO on a title the model rates below the market (US 25 of 28, global 32 of 39). Variants (3c, 10c) look the same. The 6h-window rows are dominated by single $5k fills and are not evidence.
Calibration: the model's candidate-level Brier score is worse than the market's first print (US 0.0434 vs 0.0309, global 0.0382 vs 0.0339), so it does not price better overall.

## Verdict
NOT a pass. US is positive in both halves but the held-out half's interval includes zero and the whole-sample interval barely excludes it ($0.07 to $3.81 per event); global is positive only in the held-out half and flat in the first half. At the best reading it is about $1-3 per event on stakes of $10-30 a bet. Unknown, settled by forward data: the recorder (daily lists and books) is specified in agent/tasks/TASK-netflix-recorder-2026-11-10.md; pre-registered forward test = this exact rule (US, 5c, 2h, NO-side as it falls out), judged once at 40 forward events.
Confidence 7/10.
