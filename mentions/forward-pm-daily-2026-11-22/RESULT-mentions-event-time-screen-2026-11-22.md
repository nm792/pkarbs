# Mentions event-time variants (R-051): OFF-PRIME screen on public trade data, 22 Nov ~16:00Z
Code it/mentions_pm_event_time.py (8 offline checks pass). Sets: events that CLOSED in the last 7 days (15 resolved events) and 30 days (67), ALL families. Files: et7_*.csv, et30_*.csv (variants table, per-event ranked table), event_time_*d.log.
Rules as in R-051: fair = frozen model (per-word causal base rate at listing, never refit); an own token is underpriced at p <= fair-10c (YES fair q, NO fair 1-q), p >= 5c; sized $200 per (decision, token) from a print ladder rebuilt from trades at or below the limit (FLOOR; depth otherwise UNMEASURED); $2,000/day cap per variant; fee 0.04*p*(1-p); hold to resolution. Placebo = same rule at random start times in [T-24h, T], 30 draws (7 d) / 12 draws (30 d); z = (real - placebo mean)/placebo sd.
Event time is not in the data: anchor A = Gamma endDate (tradable); anchor B = hour of peak trade volume (HINDSIGHT proxy, upper-bound screen). "during" = every 5 min over the last 6 h before T (A) or T-1h..T+2h (B).
## 30-day set (due 21:00Z): 67 events, $/day over 30 days, % of $200
| anchor | variant | events with fill | fills | stake $ | net $ | $/day | % of $200 | placebo mean +- sd | z |
|---|---|---|---|---|---|---|---|---|---|
| A | listing+1h | 21 | 77 | 782 | +399 | +13.31 | +6.66% | -15 +- 337 | 1.23 |
| B | listing+1h (same fills) | 21 | 77 | 782 | +399 | +13.31 | +6.66% | -291 +- 348 | 1.98 |
| A | T-24h | 21 | 78 | 772 | +182 | +6.06 | +3.03% | -241 +- 339 | 1.25 |
| B | T-24h | 21 | 95 | 770 | +28 | +0.92 | +0.46% | -265 +- 272 | 1.08 |
| A | T-15m | 11 | 32 | 838 | -98 | -3.28 | -1.64% | -19 +- 125 | -0.64 |
| B | T-15m | 14 | 31 | 490 | -219 | -7.29 | -3.65% | -37 +- 206 | -0.89 |
| A | T-1h | 14 | 116 | 2,084 | -279 | -9.28 | -4.64% | 42 +- 431 | -0.74 |
| A | T-6h | 16 | 68 | 1,502 | -299 | -9.97 | -4.98% | 68 +- 412 | -0.89 |
| B | T-1h | 27 | 167 | 2,022 | -478 | -15.95 | -7.97% | -379 +- 474 | -0.21 |
| B | T-6h | 23 | 130 | 2,052 | -652 | -21.72 | -10.86% | -319 +- 348 | -0.95 |
| B | during | 44 | 479 | 6,246 | -1,991 | -66.36 | -33.18% | -744 +- 787 | -1.58 |
| A | during | 20 | 599 | 9,781 | -2,368 | -78.93 | -39.46% | -394 +- 844 | -2.34 |
## 7-day set (due 18:00Z): 15 events, 7 days
Only 3 events had any fill in the listing and T-24h variants; A T-24h +$168 (+$24.06/day, 12.0%, z 0.66, 3 events), A listing+1h -$39 (-$5.58/day, -2.8%, z -0.44); T-6h, T-1h, T-15m and during (anchor A) had NO fills (0 prints at or below fair-10c); anchor B: T-15m -$47, T-24h -$59, T-1h -$132, T-6h -$211, during -$881 (-$125.88/day, z -3.35). Full rows: et7_variants.csv. 7 days is too short to rank anything (3 events with fills).
## Reading (not a verdict; significance used to rank, not to kill)
1. Ranked: **listing + 1 h with $200 sizing on every underpriced own token is the only variant above zero in both anchors (+$13.31/day = 6.7% of $200 over 30 days, z 1.2 to 2.0)**; T-24h second (+$6.06, 3.0%, z 1.25). The frozen rule's one-print sizing gave +$2.00/day (1.0%) on the same 30 days (P-MEN-1520): taking every underpriced token (not just the first print) is what lifts it, and the stake is only $782 over 30 days, so depth is the limit.
2. **Every event-time variant (T-6h, T-1h, T-15m, during) is negative with the frozen model**: prices at or below fair-10c near the event are mostly right, the base rate is stale by then (z -2.3 for "during", anchor A). The volume at event time (P-MEN-1520: $279K in the last 24 h before end) is real, but the frozen listing-time fair value does not beat it. An event-time test needs a fair value that uses event information (live transcript or live count), which is a different model, not tested here.
3. Caveats: FLOOR fills (only prints that happened; an ask that never printed is invisible; a printed ask may not have been lift-able at decision time), 67 events, 12 placebo draws, anchors are assumptions, no per-family split in this table (per-event ranked csv has family). Trump rallies drive both the best and the worst event rows (+$613 and -$1,024 in single events under "during").
