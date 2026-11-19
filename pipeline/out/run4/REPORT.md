# Stage-1 screen: run4

Run `run4`, commit `pending`, events file `events_deep.jsonl (13,149 closed events from 70 daily-or-faster series, Mar-Nov 2026, series_slug pull)` (69 families with >=5 closed events, window 240 days), out `pipeline/out/run4`.

Passed freq (gamma series recurrence = daily or faster, i.e. polymarket.com/new?_r=daily) and vol (median >= min): 69 families; top 69 by total volume were sampled (<= 220 events each, top 2 markets per event).

## Three-criteria ranking (rank sum f+v+l, lower is better)

Late move = 1 - mean price of the eventual winner's own token 15 minutes before the scheduled end time (gamma endDate), also shown at 60 and 5 minutes. Own-token last print only, never 1 minus the other side. A winner still far from 1 shortly before the scheduled close means the market was pricing the result inefficiently or late.

| family | ev/day | median vol $ | winner px T-60 / T-15 / T-5 | share winner<0.5 at T-15 | ranks f/v/l | mkts | n |
|---|---|---|---|---|---|---|---|
| series:spy-daily-up-or-down | 0.69 | 39,492 | 0.88 / 0.91 / 0.94 | 0.07 | 18/8/19 | 165 | 165 |
| series:meta-multi-strikes-daily | 0.71 | 2,875 | 0.84 / 0.89 / 0.91 | 0.07 | 5/29/12 | 132 | 130 |
| series:gold-up-or-down-15m | 53.26 | 255 | 0.51 / 0.51 / 0.68 | 0.13 | 1/47/1 | 220 | 46 |
| series:spx-daily-up-or-down | 0.68 | 94,786 | 0.88 / 0.91 / 0.93 | 0.09 | 30/3/18 | 220 | 220 |
| series:spy-daily-close-uo | 0.69 | 36,660 | 0.87 / 0.91 / 0.93 | 0.05 | 29/10/17 | 292 | 292 |
| series:spcx-daily-up-or-down | 0.70 | 463 | 0.84 / 0.86 / 0.90 | 0.07 | 7/43/6 | 100 | 96 |
| series:dxy-daily-up-or-down | 0.71 | 31 | 0.76 / 0.84 / 0.90 | 0.08 | 6/50/5 | 66 | 38 |
| series:gold-up-or-down-1h | 13.39 | 0 | 0.54 / 0.58 / 0.65 | 0.43 | 2/62/2 | 220 | 44 |
| series:aapl-daily-up-down | 0.68 | 4,169 | 0.86 / 0.88 / 0.92 | 0.10 | 39/22/7 | 220 | 220 |
| series:meta-daily-up-down | 0.68 | 4,072 | 0.84 / 0.89 / 0.92 | 0.07 | 33/23/13 | 220 | 219 |
| series:silver-up-or-down-1h | 13.39 | 0 | 0.54 / 0.62 / 0.64 | 0.41 | 3/63/3 | 220 | 37 |
| series:dissent-at-fed-meeting | 0.02 | 81,537 | 0.70 / 0.69 / 0.70 | 0.32 | 63/5/4 | 22 | 22 |
| series:tsla-daily-up-down | 0.68 | 4,688 | 0.87 / 0.92 / 0.94 | 0.05 | 32/21/23 | 220 | 220 |
| series:dow-jones-daily-up-or-down | 0.68 | 2,366 | 0.84 / 0.88 / 0.91 | 0.09 | 38/31/10 | 220 | 220 |
| series:oil-daily-up-or-down | 0.69 | 20,997 | 0.93 / 0.97 / 0.98 | 0.01 | 26/11/44 | 160 | 160 |
| series:nvda-daily-up-down | 0.68 | 5,345 | 0.88 / 0.92 / 0.94 | 0.06 | 37/20/24 | 220 | 220 |
| series:googl-daily-up-down | 0.68 | 3,794 | 0.87 / 0.93 / 0.95 | 0.04 | 31/25/26 | 220 | 220 |
| series:gold-daily-up-or-down | 0.69 | 9,586 | 0.91 / 0.95 / 0.97 | 0.01 | 27/18/37 | 164 | 164 |
| series:msft-daily-up-down | 0.68 | 3,532 | 0.88 / 0.91 / 0.95 | 0.07 | 35/27/20 | 220 | 220 |
| series:wti-daily-close-uo | 0.68 | 39,575 | 0.85 / 0.93 / 0.95 | 0.05 | 49/7/27 | 284 | 284 |
| series:us-gas-price-daily | 1.00 | 3,216 | 0.98 / 0.98 / 0.98 | 0.01 | 4/28/51 | 68 | 68 |
| series:mu-daily-up-or-down | 0.69 | 554 | 0.86 / 0.91 / 0.94 | 0.05 | 20/42/22 | 120 | 118 |
| series:nflx-daily-up-or-down | 0.68 | 2,059 | 0.86 / 0.90 / 0.92 | 0.05 | 36/34/15 | 220 | 220 |
| series:russell-2000-daily-up-or-down | 0.68 | 2,228 | 0.84 / 0.88 / 0.89 | 0.07 | 46/33/8 | 220 | 216 |
| series:silver-daily-up-or-down | 0.69 | 5,358 | 0.93 / 0.96 / 0.97 | 0.01 | 28/19/40 | 164 | 163 |
| series:coin-daily-up-or-down | 0.69 | 802 | 0.90 / 0.93 / 0.95 | 0.03 | 17/39/32 | 208 | 206 |
| series:usdjpy-daily-up-or-down | 0.70 | 10 | 0.79 / 0.92 / 0.96 | 0.02 | 9/54/25 | 92 | 44 |
| series:hood-daily-up-or-down | 0.69 | 1,582 | 0.89 / 0.93 / 0.95 | 0.03 | 25/35/29 | 207 | 206 |
| series:amzn-daily-up-down | 0.68 | 3,557 | 0.89 / 0.93 / 0.95 | 0.04 | 34/26/30 | 220 | 220 |
| series:pltr-daily-up-or-down | 0.68 | 2,743 | 0.88 / 0.91 / 0.93 | 0.05 | 43/30/21 | 220 | 220 |
| series:open-daily-up-or-down | 0.68 | 1,562 | 0.84 / 0.90 / 0.92 | 0.07 | 44/36/14 | 218 | 211 |
| series:spx-open-daily-up-or-down | 0.69 | 36,940 | 1.00 / 1.00 / 1.00 | 0.00 | 24/9/63 | 207 | 207 |
| series:ewy-daily-up-or-down | 0.69 | 394 | 0.90 / 0.94 / 0.95 | 0.03 | 19/44/33 | 165 | 152 |
| series:abnb-daily-up-or-down | 0.48 | 745 | 0.84 / 0.88 / 0.91 | 0.05 | 50/40/9 | 193 | 186 |
| series:natural-gas-daily-up-or-down | 0.68 | 3,893 | 0.89 / 0.93 / 0.95 | 0.05 | 48/24/28 | 161 | 152 |
| series:eurusd-daily-up-or-down | 0.70 | 11 | 0.93 / 0.96 / 0.96 | 0.03 | 10/52/39 | 92 | 38 |
| series:trump-truth-social | 0.29 | 86,271 | 0.94 / 0.96 / 0.98 | 0.03 | 57/4/41 | 160 | 160 |
| series:fed-3-parlay | 0.02 | 911,692 | 0.95 / 0.96 / 0.96 | 0.00 | 62/2/38 | 16 | 16 |
| series:nya | 0.68 | 201 | 0.81 / 0.89 / 0.93 | 0.06 | 45/48/11 | 220 | 123 |
| series:rklb-daily-up-or-down | 0.48 | 1,540 | 0.87 / 0.90 / 0.93 | 0.06 | 51/37/16 | 192 | 184 |
| series:elon-tweets-48h | 0.43 | 1,027,257 | 0.93 / 0.99 / 1.00 | 0.00 | 52/1/53 | 278 | 276 |
| series:ted-cruz-daily-tweets | 0.29 | 14,201 | 0.90 / 0.93 / 0.96 | 0.05 | 58/17/31 | 138 | 138 |
| series:usdtry-daily-up-or-down | 0.70 | 10 | 0.94 / 0.95 / 0.96 | 0.04 | 14/59/34 | 91 | 26 |
| series:usdbrl-daily-up-or-down | 0.70 | 11 | 0.96 / 0.98 / 0.99 | 0.00 | 11/53/46 | 92 | 35 |
| series:elon-tweet-daily | 0.10 | 14,576 | 0.95 / 0.95 / 0.95 | 0.06 | 61/15/35 | 73 | 72 |
| series:zelenskyy-tweets | 0.29 | 20,572 | 0.92 / 0.98 / 0.99 | 0.00 | 55/12/48 | 136 | 136 |
| series:spy-open-daily-up-or-down | 0.70 | 102 | 0.99 / 0.99 / 0.99 | 0.00 | 8/49/59 | 83 | 80 |
| series:usdchf-daily-up-or-down | 0.70 | 10 | 0.95 / 0.98 / 0.98 | 0.00 | 13/58/45 | 92 | 40 |
| series:whitehouse-daily-tweets | 0.29 | 47,244 | 0.97 / 1.00 / 1.00 | 0.00 | 53/6/60 | 138 | 138 |
| series:usdnok-daily-up-or-down | 0.70 | 10 | 0.94 / 0.97 / 0.98 | 0.00 | 16/61/43 | 92 | 31 |
| series:gbpusd-daily-up-or-down | 0.69 | 10 | 0.94 / 0.97 / 0.97 | 0.03 | 23/56/42 | 91 | 30 |
| series:cz-tweets | 0.29 | 18,208 | 0.97 / 0.98 / 0.99 | 0.01 | 59/14/50 | 136 | 136 |
| series:khamenei-daily-tweets | 0.29 | 20,146 | 0.99 / 0.99 / 0.99 | 0.00 | 54/13/56 | 138 | 138 |
| series:usdkrw-daily-up-or-down | 0.70 | 10 | 0.99 / 0.99 / 0.99 | 0.00 | 12/57/54 | 92 | 33 |
| series:nycmayor-tweets | 0.29 | 14,323 | 0.99 / 0.99 / 0.99 | 0.00 | 56/16/52 | 136 | 136 |
| series:usdsek-daily-up-or-down | 0.69 | 10 | 0.97 / 0.98 / 0.98 | 0.00 | 22/55/47 | 91 | 34 |
| series:white-house-call-a-full-lid | 0.24 | 2,365 | 0.95 / 0.95 / 0.96 | 0.03 | 60/32/36 | 96 | 95 |
| series:usdmxn-daily-up-or-down | 0.69 | 12 | 0.99 / 0.99 / 0.99 | 0.00 | 21/51/57 | 91 | 30 |
| series:usdzar-daily-up-or-down | 0.70 | 10 | 0.98 / 0.99 / 0.99 | 0.00 | 15/60/55 | 92 | 41 |
| series:dax-daily-up-or-down | 0.68 | 375 | 0.98 / 0.98 / 0.98 | 0.01 | 41/45/49 | 215 | 214 |
| series:hang-seng-daily-up-or-down | 0.68 | 1,107 | 0.99 / 1.00 / 1.00 | 0.00 | 40/38/62 | 211 | 208 |
| series:ftse-100-daily-up-or-down | 0.68 | 362 | 0.99 / 0.99 / 0.99 | 0.00 | 42/46/58 | 217 | 215 |
| series:nik-daily-up-or-down | 0.68 | 693 | 1.00 / 1.00 / 1.00 | 0.00 | 47/41/61 | 206 | 202 |

## Signal IC (ex-ante, decision = end time minus H, fill = first BUY print after)

Cells tried: 105. Benjamini-Hochberg q=0.10 discoveries on out-of-sample p: 1.

Top 15 cells by out-of-sample IC with >=6 test buckets (sign chosen on train only):

| family | H | signal | n events | IC all | IC train | IC test | t test | p test | BH |
|---|---|---|---|---|---|---|---|---|---|
| GROUP:tweet-counts | 6h | mom4 | 255 | +0.146 | +0.109 | +0.192 | +1.93 | 0.078 | no |
| GROUP:finance-daily-updown | 10m | volratio | 379 | -0.184 | -0.221 | +0.178 | +2.06 | 0.054 | no |
| GROUP:tweet-counts | 6h | price | 255 | +0.082 | +0.040 | +0.142 | +1.11 | 0.288 | no |
| GROUP:finance-daily-updown | 10m | imbalance | 379 | -0.073 | -0.055 | +0.130 | +1.33 | 0.201 | no |
| GROUP:tweet-counts | 6h | mom1 | 255 | +0.070 | +0.034 | +0.120 | +0.90 | 0.387 | no |
| GROUP:finance-daily-updown | 1h | price | 1117 | +0.075 | +0.057 | +0.105 | +2.25 | 0.035 | no |
| GROUP:tweet-counts | 6h | ntrades | 255 | +0.041 | +0.008 | +0.103 | +1.22 | 0.247 | no |
| GROUP:finance-daily-updown | 6h | mom1 | 3472 | +0.085 | +0.073 | +0.102 | +3.72 | 0.000 | yes |
| GROUP:finance-daily-updown | 6h | price | 3472 | +0.074 | +0.059 | +0.099 | +3.00 | 0.003 | no |
| GROUP:finance-daily-updown | 6h | mom4 | 3472 | +0.045 | +0.009 | +0.096 | +2.75 | 0.008 | no |
| GROUP:tweet-counts | 6h | volratio | 255 | +0.047 | +0.012 | +0.096 | +0.97 | 0.353 | no |
| GROUP:tweet-counts | 24h | ntrades | 438 | -0.066 | -0.039 | +0.090 | +1.53 | 0.147 | no |
| GROUP:finance-daily-updown | 10m | range | 379 | -0.079 | -0.056 | +0.089 | +0.78 | 0.444 | no |
| GROUP:tweet-counts | 24h | range | 438 | -0.053 | -0.017 | +0.088 | +1.46 | 0.165 | no |
| GROUP:finance-daily-updown | 10m | mom1 | 379 | -0.125 | -0.157 | +0.087 | +0.64 | 0.529 | no |

## Follow-up on the one BH discovery (finance daily up/down group, H = 6 h before close, mom1)
Run by an ad-hoc script on the same cached trades (not yet committed as a module; numbers are unsupported until it is). Test = last 40% of markets by time, one token per market, 91 days.
- Buy the token that rose more than 2c over the prior 6 h (own first BUY print after decision): n 864, 95 days, ROI +3.6% (95% CI -0.3% to +7.1%, clustered by day), fee-adjusted +2.7%, mean fill 0.70. Not significant.
- Buy the opposite token (own ask) when the other fell more than 2c: n 826, ROI +3.6% (CI -0.5% to +7.3%).
- Buying the token that FELL more than 2c: ROI -11.0% (CI -20.8% to -1.7%): cheap falling tokens lose; that is the IC.
- The earlier 1 h mom1 lead on a 30-day sample (IC +0.41, t 6.8, 13 days) vanished with deep history (IC +0.046, p 0.42): small-sample noise.
