# Box office, 2nd to 8th weekend brackets: first pass of the locked test (10 Nov 2026)

Thread "Find and test MrBeast-style markets". Scripts and output in forecast-edges/mrbeast-style/ (bo_fetch.py, bo_bt.py, bo_bt_output.txt, bom_weekends_2024W21_2026W44.json.gz).

## Inventory
Polymarket has 367 resolved box office events ($134M listed volume): 267 opening weekend, about 87 later weekends (2nd to 8th), 13 weekly totals. Opening weekends need tracking data (paid), so NOT tested. Later weekends have a free input: Box Office Mojo weekend pages (free, complete, fetched 2024W21 to 2026W44, 128 weekends).

## Model (fixed before looking at results)
Log ratio of this weekend to the previous weekend gross, normal, mean and sd per weekend bucket (2nd, 3rd, 4th+) fitted on the first half of events by time. Bracket probabilities from the normal. Strict availability: decision time is market start + 1h and must be on or after the Wednesday following the previous weekend (final numbers out). 26 events dropped by this rule.

## Locked test
First BUY print inside the 2h or 6h window with edge of at least 5c or 10c (own side: YES price vs q, NO price vs 1-q), full print size, held to resolution, one unit per event. Placebo: random BUY print, same side and price within 5c, drawn from other events. 57 events with data, 29 in the test half.

| Variant | Bets | P&L / cost | Placebo | z | per-event CI | Test half z, CI |
|---|---|---|---|---|---|---|
| 2h, 5c | 16 | $85 / $139 | $31 | 5.7 | [0.12, 3.10] | 4.7, [0.21, 4.67] |
| 2h, 10c | 15 | $81 / $131 | $32 | 5.5 | [0.01, 3.10] | 4.7, [-0.01, 4.32] |
| 6h, 5c | 22 | $168 / $323 | $25 | 5.4 | [0.91, 5.43] | 4.0, [0.75, 5.58] |
| 6h, 10c | 21 | $171 / $300 | $19 | 5.3 | [0.97, 5.49] | 3.9, [0.46, 5.19] |

Checks: oracle +$168 (z 12.9), anti-oracle -$369 (z -22.9): the placebo and sign logic work. All 8 variants positive.

## What this is and is not
First series to pass the locked test on the pre-set criteria. It is NOT yet an edge: 57 events, 9 to 10 events behind each fitted bucket, one model family. Size is tiny: taking every qualifying print in 6h would have made about $949 on $2,787 over the whole sample. Median event notional $20k. Opening weekends carry the volume and are not testable for free.

## Next
Forward test on new later-weekend events (rule: 6h, 5c, first qualifying print), judged once at 30 forward events using the same script, which can be re-run from public history (no recorder needed). About 1.5 events a week, so roughly 20 weeks. Cheaper check: pull 2023 and earlier weekend pages for more history of drop ratios (events before 2024 are few).
