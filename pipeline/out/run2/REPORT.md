# Stage-1 screen: run2

Run `run2`, commit `af9d5e6b1c`, events file `events.jsonl (161,153 closed events, endDate 20 Oct-19 Nov 2026)` (104 families with >=5 closed events, window 30 days), out `/home/user/pk_cache/run2`.

Passed freq (gamma series recurrence = daily or faster, i.e. polymarket.com/new?_r=daily) and vol (median >= min): 66 families; top 50 by total volume were sampled (<= 60 events each, top 2 markets per event).

## Three-criteria ranking (rank sum f+v+l, lower is better)

Late move = 1 - mean price of the eventual winner's own token 15 min before T*, where T* = last winner print below 0.95 (hindsight anchor: when the market finished moving). The clock columns anchor on the market endDate instead (known ex ante; for sports it is near the scheduled start, so those are pre-game prices).

| family | ev/day | median vol $ | winner px endDate-60 / -15 / -5 | share winner<0.5 at endDate-15 | winner px T*-60 / -15 / -5 | ranks f/v/l | mkts | n |
|---|---|---|---|---|---|---|---|---|
| series:spy-daily-close-uo | 0.7 | 35,341 | 0.81 / 0.88 / 0.91 | 0.11 | 0.77 / 0.78 / 0.80 | 4/4/18 | 44 | 41 |
| series:meta-multi-strikes-daily | 0.7 | 2,314 | 0.81 / 0.87 / 0.91 | 0.09 | 0.67 / 0.71 / 0.75 | 7/16/4 | 44 | 37 |
| series:us-gas-price-daily | 1.0 | 3,331 | 0.99 / 0.99 / 0.99 | 0.02 | 0.75 / 0.78 / 0.80 | 1/15/17 | 60 | 36 |
| series:white-house-call-a-full-lid | 0.9 | 1,333 | 0.99 / 0.99 / 0.99 | 0.00 | 0.76 / 0.76 / 0.78 | 2/18/13 | 28 | 23 |
| series:msft-daily-up-down | 0.7 | 1,233 | 0.89 / 0.90 / 0.95 | 0.05 | 0.68 / 0.73 / 0.78 | 13/19/5 | 22 | 20 |
| series:spx-daily-up-or-down | 0.7 | 43,934 | 0.94 / 0.98 / 0.98 | 0.00 | 0.84 / 0.90 / 0.93 | 3/3/33 | 22 | 22 |
| series:russell-2000-daily-up-or-down | 0.7 | 908 | 0.78 / 0.80 / 0.82 | 0.20 | 0.65 / 0.63 / 0.62 | 11/28/1 | 22 | 17 |
| series:spx-open-daily-up-or-down | 0.7 | 8,022 | 1.00 / 1.00 / 1.00 | 0.00 | 0.70 / 0.83 / 0.84 | 6/12/26 | 22 | 21 |
| series:wti-daily-close-uo | 0.6 | 19,962 | 0.86 / 0.93 / 0.94 | 0.06 | 0.73 / 0.76 / 0.78 | 27/7/11 | 36 | 35 |
| series:spy-daily-up-or-down | 0.7 | 16,023 | 0.94 / 0.97 / 0.98 | 0.00 | 0.81 / 0.86 / 0.91 | 5/9/31 | 22 | 22 |
| series:gold-daily-up-or-down | 0.7 | 3,341 | 0.94 / 0.93 / 0.97 | 0.05 | 0.82 / 0.82 / 0.84 | 9/14/23 | 22 | 22 |
| series:cz-tweets | 0.3 | 23,161 | 0.94 / 0.93 / 0.95 | 0.06 | 0.77 / 0.76 / 0.82 | 32/5/12 | 18 | 17 |
| series:tsla-daily-up-down | 0.7 | 1,106 | 0.88 / 0.91 / 0.88 | 0.05 | 0.75 / 0.75 / 0.76 | 17/24/9 | 22 | 22 |
| series:nvda-daily-up-down | 0.7 | 3,572 | 0.92 / 0.95 / 0.97 | 0.05 | 0.77 / 0.85 / 0.87 | 8/13/30 | 22 | 22 |
| series:pltr-daily-up-or-down | 0.7 | 1,137 | 0.83 / 0.84 / 0.86 | 0.18 | 0.71 / 0.77 / 0.77 | 12/23/16 | 22 | 19 |
| series:oil-daily-up-or-down | 0.6 | 2,203 | 0.88 / 0.97 / 0.97 | 0.00 | 0.72 / 0.74 / 0.71 | 28/17/7 | 18 | 18 |
| series:elon-tweets-48h | 0.4 | 698,086 | 0.91 / 1.00 / 1.00 | 0.00 | 0.77 / 0.82 / 0.83 | 29/1/25 | 26 | 25 |
| series:dow-jones-daily-up-or-down | 0.7 | 389 | 0.77 / 0.80 / 0.81 | 0.23 | 0.67 / 0.68 / 0.69 | 21/32/2 | 22 | 18 |
| series:googl-daily-up-down | 0.7 | 916 | 0.90 / 0.92 / 0.94 | 0.09 | 0.76 / 0.76 / 0.78 | 19/27/10 | 22 | 20 |
| series:mu-daily-up-or-down | 0.7 | 1,201 | 0.96 / 0.98 / 0.98 | 0.00 | 0.80 / 0.83 / 0.85 | 10/21/27 | 22 | 21 |
| series:amzn-daily-up-down | 0.7 | 1,076 | 0.83 / 0.89 / 0.87 | 0.05 | 0.74 / 0.80 / 0.79 | 14/25/19 | 22 | 21 |
| series:ted-cruz-daily-tweets | 0.3 | 20,151 | 0.87 / 0.90 / 0.90 | 0.06 | 0.80 / 0.82 / 0.81 | 31/6/22 | 18 | 17 |
| series:nflx-daily-up-or-down | 0.7 | 1,225 | 0.90 / 0.92 / 0.94 | 0.05 | 0.74 / 0.82 / 0.83 | 15/20/24 | 22 | 22 |
| series:spcx-daily-up-or-down | 0.7 | 421 | 0.82 / 0.82 / 0.83 | 0.14 | 0.72 / 0.69 / 0.66 | 25/31/3 | 22 | 17 |
| series:trump-truth-social | 0.3 | 74,791 | 0.96 / 0.95 / 1.00 | 0.06 | 0.82 / 0.84 / 0.87 | 30/2/29 | 18 | 18 |
| series:silver-daily-up-or-down | 0.7 | 1,193 | 0.95 / 0.94 / 0.95 | 0.05 | 0.77 / 0.82 / 0.82 | 18/22/21 | 22 | 22 |
| series:rklb-daily-up-or-down | 0.7 | 311 | 0.90 / 0.93 / 0.93 | 0.05 | 0.61 / 0.73 / 0.74 | 24/34/6 | 22 | 18 |
| series:ewy-daily-up-or-down | 0.7 | 467 | 0.92 / 0.95 / 0.96 | 0.05 | 0.72 / 0.76 / 0.77 | 23/30/14 | 22 | 16 |
| series:coin-daily-up-or-down | 0.7 | 341 | 0.91 / 0.91 / 0.94 | 0.05 | 0.75 / 0.74 / 0.78 | 26/33/8 | 22 | 18 |
| series:aapl-daily-up-down | 0.7 | 879 | 0.91 / 0.94 / 0.97 | 0.00 | 0.73 / 0.81 / 0.85 | 20/29/20 | 22 | 21 |
| series:meta-daily-up-down | 0.7 | 1,028 | 0.91 / 0.97 / 0.98 | 0.00 | 0.74 / 0.83 / 0.86 | 16/26/28 | 22 | 21 |
| series:hood-daily-up-or-down | 0.7 | 282 | 0.91 / 0.91 / 0.91 | 0.05 | 0.71 / 0.76 / 0.78 | 22/35/15 | 22 | 17 |
| series:zelenskyy-tweets | 0.3 | 17,639 | 0.98 / 0.97 / 0.98 | 0.00 | 0.89 / 0.88 / 0.89 | 33/8/32 | 18 | 16 |
| series:whitehouse-daily-tweets | 0.3 | 14,634 | 0.98 / 0.99 / 1.00 | 0.00 | 0.86 / 0.90 / 0.91 | 34/10/34 | 18 | 17 |
| series:nycmayor-tweets | 0.3 | 13,259 | 0.98 / 0.98 / 0.97 | 0.00 | 0.90 / 0.91 / 0.92 | 35/11/35 | 18 | 16 |

Caution: T* uses hindsight, and a live market that resolves in play is expected to be uncertain until late. A large late gap alone is not evidence of mispricing; the ex-ante IC table below is the test.

## Signal IC (ex-ante, decision = end time minus H, fill = first BUY print after)

Cells tried: 56. Benjamini-Hochberg q=0.10 discoveries on out-of-sample p: 0.

Top 15 cells by out-of-sample IC with >=6 test buckets (sign chosen on train only):

| family | H | signal | n events | IC all | IC train | IC test | t test | p test | BH |
|---|---|---|---|---|---|---|---|---|---|
