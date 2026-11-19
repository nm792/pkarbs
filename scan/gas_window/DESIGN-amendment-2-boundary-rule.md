# Amendment 2: boundary rule, pre-registered 19 Nov 2026 before the 20 Nov event lists (about 15:03Z)

Goal: find an automated, un-publicised edge worth $500/day. Settled by Nick 19 Nov: the AAA page updates about 03:15 ET; each next-day gas event lists at 10:01 to 10:18 ET on D-1 (first price on the 1-minute history), right after the 10:00 ET print; at listing the latest public print is D-1's. SETTLED.md e2a25c41beffd3f4438590a691fc2ed07402838b (A7: this note and the recorder never place or stage orders; fills below are judged only against recorded books and prints; A8: nothing inferred from books read after the decision).

## Rule (fixed now, no tuning on forward days)
1. Inputs known at listing: D-1 print (AAA, 10:00 ET), the ridge nowcast from nowcast.py (v0, spot_lag 2, alpha 10, train from 2026-03-26), the listed bucket edges.
2. Boundary margin m = distance in cents from the nowcast mean to the nearest listed edge, measured inside the top bucket. Interior buckets are 1c wide so m is at most 0.5c; the 0.5c cutoff therefore selects only a bucket whose single edge the mean clears by at least 0.5c, i.e. an open-ended outer bucket (less-than or plus bucket) or a mean exactly at the middle of a 1c bucket. Trade only when m >= 0.5c. (Finding 19 Nov: 9 of 28 events qualify; distance under 0.5c on the other 19.)
3. Bucket = the nowcast top bucket. Model probability p = nowcast mass in that bucket.
4. Entry: an immediate resting bid on that bucket's YES token in the first seconds after listing at the seed price (about 0.50); no 10-minute taker window as the primary rule. Secondary, reported separately: taker buy at the token's own ask if p minus ask is at least 0.05.
5. Sizing: quarter Kelly: stake = 0.25 * bankroll * (p - b) / (1 - b), b = bid price, capped by the depth recorded at that price. Zero if p <= b.
6. Listing time to the second: pm_gas_books.py polls Gamma events?slug= for the next day's event until it exists; the first book state per token (own asks, bids, depth) is stored. The cutoff 0.5c, quarter Kelly and the 0.05 gap are fixed here.

## Evidence so far (exploratory, 19 Nov, scripts in this folder; not a pass)
- Hit rate of the nowcast top bucket by margin, out of sample 26 May to 21 Oct (144 days, ladder assumed): margin >= 0.5c hit 71% (n=17, ladder -2..+2), 88% (n=24, ladder -1..+3); margin < 0.5c hit 43-44%. The real PM ladder starts at floor(prev cents) minus 1 or 2 and has 6 or 7 edges, so ladder assumptions matter. In-sample 22 Oct to 18 Nov with the real ladders: 9 qualifying events, 7 hit (78%).
- Bid fill: on those 9 days there is no YES SELL print at any price at or below 0.90 within 1 hour of listing (0 of 9). First prints are taker BUYs at 0.79 to 0.97 (6 Nov at lag 0 minutes, 13 Nov at 8 minutes, 18 Nov at 7 minutes); 15 Nov first print 0.05 at 132 minutes. A resting bid near 0.50 would not have filled. Buying at those first prints loses about 10% on the nine days (hit 78% against prices 0.79 to 0.97). The rule's 0.05 gap test fires on 0 of 9.
- Verdict before forward data: hit rate is real, price already reflects it on the days the rule picks. Forward test decides; prices and fills come from tonight's recorder only.

## Forward test and reporting
Daily from the 20 Nov listing: record listing second, first book per token, p, m, whether the rule fires, bid fill (a SELL print or a book crossing at or below the bid after the recorded time), quarter-Kelly stake and P&L at real asks, with and without 14 Nov in any rollup. Read once at n=30 trades fired or 19 Dec, whichever is later. Pass bar unchanged (Amendment 1): paired lower bound above zero and the economic bar noted as unreachable on this volume.
