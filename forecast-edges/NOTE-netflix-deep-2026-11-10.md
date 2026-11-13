# Netflix deep dive (10 Nov 2026)
Measured = computed. No orders. Scripts/outputs: forecast-edges/mrbeast-style/nf_full.py, nf_full_output.txt (every variant).

## 1. Every Netflix market
Polymarket: 426 events, 7,660 markets, $16.6M lifetime. 391 resolved weekly rank events: #1 and #2, global and US, movie and show (8 series, 47-55 events each, 57 weeks Aug 2025 to Nov 2026), about $16.2M. Also 20 "how many views will #1 movie/show have" events (about $0.2M) and a few one-offs (earnings call words, operating margin, Zelenskyy show). No separate top-10-position or specific-title series exist on Polymarket.
Kalshi (reached via TinyFish fetch; container blocked): 11 live weekly series, each 10 events since 8 Sep 2026 (one #2 show series from 9 Dec 2025): US movie #1 1.04M contracts, US show #1 1.13M, US movie #2 0.25M, US show #2 0.41M, global movie #1 0.30M, global show #1 0.16M, global #2 movie 0.14M, #2 show 0.09M, #1 show views 0.44M, #1 movie views 0.49M = about 4.5M contracts (each pays $1) over 10 weeks. KXNETFLIXRANKING and the daily series (KXNETFLIXSHOWRANKD, KXNETFLIXMOVIERANKD) have no markets. Only 10 weeks of history, so no held-out half possible; Kalshi trade history not pulled (per-market fetches through the proxy).

## 2. Model (global only)
Inputs, all from Netflix's official weekly file (239 weeks, 2021-2026): hours viewed, weeks in top 10, rank. Each title in last week's top 10 gets next-week hours = last hours x exp(Normal(mean, sd)) fitted by weeks-in-list bucket (1,2,3,4+) on weeks before the split date; Monte Carlo gives P(title is #1 or #2); new-entrant share from history (movie 43%/45% for #1/#2, show 31%/27%). Bets only on listed titles.
Not reachable and therefore NOT used: trailer views (YouTube), Google Trends, IMDb popularity (no per-week history), release day (no systematic free calendar), FlixPatrol daily (bot-blocked; stealth bypass refused). Runtime and views are in the file but add little on top of hours. US series have no hours in a file that fits through the fetch tool (the all-countries file is too large), so US is NOT modelled.

## 3. Locked test with the audit fixes
First qualifying print is the bet (no best-of-window), full print size, placebo matched on side and price (within 5c, same event window, 2,000 draws), each event one unit, split at 5 May 2026 (first half fits, second half is the test). Primary: threshold 5c, decision T = start+1h, 2h window. All 12 variants (threshold 3/5/10c, window 2h/6h, T = start+1h or close-72h) are in nf_full_output.txt.
Primary, test half: 47 events, 14 bets, $231 staked, +$63, matched placebo +$69 ± 6 -> -1.0 sd. Rank 1: +$37 vs +$37 (0.0 sd). Rank 2: +$26 vs +$32 (-1.6 sd).
Across the variants the test-half excess against the matched placebo ranges -1.4 to +0.6 sd; first-half best +2.2 sd (6h window) that is gone in the test. The 6h-window test is one $5k fill deciding everything (real and placebo identical). None pass. Wins: the model picks the same side/price as a random print, so it adds nothing beyond price.

## 4. Size that could be traded (Polymarket, 8 series together, 57 weeks)
BUY notional printed in the first 2h after start+1h: median $609/week (mean $1,578). First 6h: median $3,334/week. Anything after start+1h until close: median $114k/week, but that is late, when the answer is mostly priced. Lifetime volume: median $190k/week; last 10 weeks median $90k/week. 88 of 106 global events had no BUY print in the 2h window. Kalshi: about 450k contracts/week across the 11 series (roughly $100-200k notional/week, not measured).

## 5. Verdict
No pass; the model is not better than the market at any decision time tested. Unknown: US markets (not modelled), Kalshi (10 weeks, no fills data), release-timing and trend inputs. Confidence 7/10.
