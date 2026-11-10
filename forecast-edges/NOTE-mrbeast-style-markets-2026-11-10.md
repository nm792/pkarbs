# MrBeast-style markets: full list and locked test (10 Nov 2026)

Result: NONE PASSED. Measured = computed from Polymarket gamma and data-api trades. No orders. Scripts and raw outputs in forecast-edges/mrbeast-style/.

## 1. List of series (Polymarket; found by 40 tag searches plus 30 keyword searches, 2,970 events)
Polymarket has no complete listing endpoint, so "complete" means everything those searches return. Volume is lifetime.
| Family | Events | Volume | Tested here |
|---|---|---|---|
| MrBeast views, day N (1 to 6) | 133 | $63.7M | YES |
| MrBeast views, week 1 | 49 | $32.2M | YES |
| MrBeast Gaming views | 18 | $1.7M | YES (in the same run) |
| MrBeast channel milestones (subs, billions of views by month-end) | 23 | $14.5M | no, see below |
| MrBeast say-words | 33 | $1.7M | no (not a count) |
| Other YouTube video views (GTA VI, Ronaldo, halftime) | 54 | $15.5M | no, one-offs |
| Netflix weekly top / #2, global + US, movie + show | 426 | $16.6M | YES (persistence) |
| Spotify weekly #1/#2 song | 180 | $115M (mostly 3 big annual events) | YES (persistence, weekly part) |
| Apple App Store #1/#2 free and paid, daily | 256 | $15.7M | YES (persistence) |
| Billboard Hot 100 / 200 weekly #1/#2 | 147 | $8.8M | YES (persistence) |
| OpenRouter #1/#2/#3 lab weekly | 48 | $7.0M | YES (persistence, 9 windows per rank) |
| Twitch / stream viewers / Kai / Speed | 72 | $16.4M | no, forecast-edges thread covers it |
| Truth Social / X post counts | 122 | $21.0M | no, forecast-edges thread covers it |
| Podcast and TV mention words (Rogan, All-In, Love Island...) | 204 | $83M | no (not a count; would need transcripts) |
| Rotten Tomatoes score | 169 | $13.3M | no |
| Box office | 400 | $389M | tested in earlier note, no stable gap |
| Google most-searched | 68 | $92M | no, mostly annual one-offs |
Full table: polymarket_inventory.txt. Volumes for MrBeast milestones: 11 monthly "billion views" and 9 monthly "million subscribers" events, $0.01-1M each.

Kalshi (reached only through the TinyFish fetch proxy, the container is blocked): 2,600 entertainment series, 104 recurring daily/weekly/monthly ones on streams, charts, Netflix, app ranking and YouTube views (kalshi_recurring_series.txt). KXMRBEAST50M/100M/100 return no markets. The one YouTube count series with repeats is KXYTVIEWSD (artist daily views): first 1,000 markets show only 3,801 contracts traded in total, nothing to fill. Not backtested.

## 2. Locked test (same for all)
Real BUY prints only, full print size, at the decision time T = market start + 1h, window 2h, edge over 5c, one bet per window (largest edge), hold to resolution, all windows with fills, history split in time order (first half fits parameters, second half is the held-out test), placebo = random BUY print from the same windows (2,000 draws). I did not change any rule after seeing results.

### MrBeast views (198 resolved events, 47 videos, Dec 2025 to Nov 2026 events; 106 windows had fills)
Model M1 (first market for a video): mean of the last 4 videos' winning bracket midpoints at the same horizon, log-normal, spread from first half (0.23). Model M2 (continuation, market for day N when day N-1 already resolved): previous day's winning bracket times the average growth ratio for that day pair (24 to 72h: x1.67 etc.), spread from first half.
| | windows | bets | stake | P&L | placebo | vs placebo |
|---|---|---|---|---|---|---|
| ALL | 106 | 80 | $987 | +$189 (+19%) | +$42 ± 563 | +0.3 sd |
| First half | 61 | 47 | $714 | +$317 | -$1 ± 560 | +0.6 sd |
| TEST half | 45 | 33 | $273 | -$128 (-47%) | +$62 ± 234 | -0.8 sd |
| M1 test | 15 | 10 | $79 | -$38 | +$31 ± 70 | -1.0 sd |
| M2 test | 30 | 23 | $194 | -$90 | +$31 ± 221 | -0.6 sd |
Threshold 10c gives the same picture (test -$125, -0.7 sd). Verdict: no edge. Both halves have wins/losses of 32/48.

### Persistence in weekly and daily rank markets (682 windows, 224 with fills)
Rule: the winner of the previous resolved event in the same series stays; probability = first-half stay rate per family and rank (Netflix #1 0.27, #2 0.20; Spotify #1 0.47; App Store #1 free 0.61; Billboard Hot 100 0.44, 200 0.29). Buy YES or NO on that outcome when the price is more than 5c away.
| | windows | bets | P&L | placebo | vs placebo |
|---|---|---|---|---|---|
| All families, all | 224 | 97 | +$1,166 on $834 | +$484 ± 388 | +1.8 sd |
| All families, first half | 144 | 58 | +$1,182 | +$373 ± 381 | +2.1 sd |
| All families, TEST half | 80 | 39 | -$16 on $191 | +$106 ± 47 | -2.6 sd |
Per family test half: Netflix -$6 (-1.1 sd), Spotify +$24 (-1.3 sd), Billboard +$31 (+1.3 sd, 8 windows), App Store +$64 (+1.5 sd, 22 windows), OpenRouter +$62 (+1.5 sd, 6 windows). Winning bets are 21 of 97: the first-half profit is a few long shots. Verdict: no edge. App Store and OpenRouter test halves are positive but tiny (22 and 6 windows) and not significant, so they are not leads.

## 3. What is not tested (so unknown)
- No hourly view counts for past videos are reachable, so a "views so far extrapolated to hour 24" model cannot be backtested. It needs the recorder (MrBeast RSS retry already pushed).
- Persistence is the crudest model. Netflix daily lists (FlixPatrol), Spotify daily charts (kworb) and Billboard streaming/sales data are public and would be the real forecast inputs; none was pulled here.
- Only 106 of 198 MrBeast windows and 224 of 682 rank windows had a BUY print in the 2-hour window; volume has fallen from $10-15M a month to about $2.5M, so even a real edge would be small.
- Kalshi history not backtested (above).

## Confidence
8/10 that nothing here is an edge on the stated models. 6/10 that the list is complete (Polymarket search only, Kalshi partial). To raise both to 9: Kalshi full series and trade history (needs the container allowlist for api.elections.kalshi.com, one network card), and per-hour view counts.
