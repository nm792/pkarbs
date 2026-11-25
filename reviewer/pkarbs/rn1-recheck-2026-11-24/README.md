# RN1 re-check and NBA post-only bid evidence (Reviewer, 24 Nov 02:58Z)

Nick 24 Nov 02:51Z: "why would we not be checking 4 in more detail?" Desk work on public data. Paper only.

## A. RN1's real fills, 23 Nov 19:40Z to 24 Nov 02:52Z (Polymarket data-api v2)
Wallet 0x2005d16a84ceefa912d4e380cd32e7ff827875ea (name "RN1"). 4,000 fills from `v2/trades?user=..&taker_only=false`. RN1 was taker on a fill if the same (tx, token, size, price, side) appears in `taker_only=true`; the rest are maker fills. This is a set difference, not an on-chain check.
- Volume $456,157 in about 7 hours. **Maker 84.4% of $** (3,377 fills, $385,054); taker 623 fills, $71,104. **Every fill is a BUY**, so it still runs resting bids only.
- Maker $ by league: NBA $79,983; EPL $78,257; NFL $52,307; Brasileirão $47,898; Serie A $44,552; LaLiga $17,283; WTA $13,409.
- NBA maker $ by market type: totals $38,830, spreads $22,714, moneylines $18,439. RN1 now quotes totals, spreads and first-half totals, not only moneylines.
- Maker fill size: median $17.9, p90 $208, max $3,737. Maker price quartiles 0.22 / 0.47 / 0.60.
- **Resolved P&L (one night, to result, noisy):** maker fills +$9,209 on $263,626 (+3.5%). NBA maker +$4,476 on $42,509 (+10.5%), EPL maker +$4,129 on $78,257 (+5.3%). Taker fills -$3,390 on $18,508 (-18.3%), of which NBA -$2,872 on $17,788. Same split as the 3 Nov decomposition: the maker side earns and the taker side loses.
- **Markouts, NBA maker fills in the 40 largest NBA markets (58% of NBA maker $), 572 fills, $40,261.** These are print-based: "market" = last print on the same token, so they are noisy in thin markets.
  - Moneylines: entry +2.10%, first minute +0.80%, to 10 min +6.81%.
  - Spreads: entry +3.32%, first minute -5.12%, to 10 min +4.66%.
  - Totals: entry -4.74%, to 10 min -3.84%. The last print is stale in thin first-half totals, e.g. paid 0.66 when the last print was 0.52.
  - So print markouts cannot judge totals. The P106e own-token books can.
- Concrete large fills: 00:32:52Z mem-cha 1H total 111.5, 1,034 sh at 0.66, resolved 1. 02:39:43Z cle-chi spread away 1.5, 5,205 sh at 0.28 (unresolved at pull). 02:34:16Z bkn-min spread home 13.5, 262 sh at 0.92, +1 min print 0.88.
- File: nba_rows.json (one row per fill: size, paid, last print, +1 min, +10 min, result).

## B. What the 6 Nov simulation did (notes/project-review-2026-11-06.md @59bec3a46b, rn1/scores/lol/bidsim)
- **Rule:** after a game event, bid at market x 0.975 post-only, hold to result. "Queue-safe" fills on public prints.
- **NBA, 429 games, by feed delay:** 0 s $25.6/game (~$184/day); 2 s $20.2; **5 s $9.6 (~$69/day, range just spans zero)**; 10 s $2.9; 30 s+ negative. The free Polymarket sports stream arrives about 5 s after the play.
- **Warning:** held-out 2026-season games were -$42/game at 0 s on 39 games.
- **Queue:** median 6,300 shares ahead of our bid, MEASURED on only 5 minutes of late-game books. This is the main uncertainty.
- **LoL resting-bid sim (3 Nov):** without event cancels, bids lose 6.2% within a minute in all 6 games. Pulling bids for 30 s after events gives +1.2%, plus about +0.4% rebate. Event-driven sellers are the whole risk.
- **Live:** 0 fills ever (LoL dry run, 62 bids, median queue 1,876 shares ahead).

## C. Facts the Nautilus spec must carry
- NBA game markets read seconds_delay = 0 (2 games, 23 Nov 09:00Z). Post-only orders are not affected by the matching delay either way.
- Fees and rebates come from each market's own feeSchedule (sports_fees_v2: rate 0.03, rebateRate 0.25 on current CS2 match markets; NBA to be read per market).
- Own-token books from P106e (running since 23 Nov 08:58Z, 20/20 tokens). Queue ahead = depth at our price at placement; fill only on trade-through at or past our price.
- Score by markout at 1 min and 10 min plus settlement (MODELLING-PRINCIPLES 12). Sequential stops (13). Capacity from measured depth (14). Event cancel window as a parameter (0, 3, 10, 30 s).

## D. Data-source breakage found while doing this (affects every PK scorer)
- **Polymarket Data API v1 is retired:** `data-api.polymarket.com/trades|activity` return HTTP 410 "Data API v1 has been retired". v2 lives at `/v2/trades` with cursor paging (`pagination.next_cursor`).
- **v2 silently ignores unknown query params:** `markets=` and `condition_ids=` returned other markets' trades; only `condition_id` (or `condition`, `conditionId`) filters. A wrong param name returns plausible but WRONG data.
- **Gamma `/events?...&limit=100` now returns 406;** limit 50 works.

Confidence 6/10. One night of RN1 fills, print-based markouts, and a maker/taker split that rests on the taker_only flag. To reach 9: P106e book-based markouts on RN1's NBA fills (same night), and an on-chain maker check on a sample.

## E. Per sport, 3 days (21 Nov 03:25Z to 24 Nov 03:25Z), added 03:29Z (Nick 03:24Z: "can this work for other sports?")
Same method. 32,942 fills; maker by the taker_only set difference. Resolved = token result from gamma. P&L is to the result, before rebates (rebates add about +0.5% per the 3 Nov decomposition).
- **All sports:** maker $5.57M = **94.7% of $**; resolved maker P&L **+$31,736 on $5.37M = +0.59%**. Taker +$21,320 on $286K (+7.4%; mostly two LaLiga/Belgian cells).
- **CORRECTION to section A:** NBA maker over 3 days is **-$1,819 on $270K (-0.7%)**, not the +10.5% of one night. Daily NBA maker P&L: 21 Nov -$4,681, 22 Nov -$7,979, 23 Nov +$5,078, 24 Nov +$5,764. One night proves nothing; the daily swings are larger than the edge.
- **Price band (answers "stale asks after the game is resolved?"):** maker fills at 0.95-0.99 made +1.03% on $476K, and at >= 0.99 -0.46% on $262K. That band is 13% of maker $ and breaks even, so the money is NOT from stale post-result quotes. The swings are in the 0.20-0.50 band (-7.8% on $1.42M) and the 0.50-0.80 band (+6.3% on $2.21M).

| league | maker $ | maker % | resolved maker P&L | 10-min markout (top-8 markets) | entry below last print | first minute |
|---|---|---|---|---|---|---|
| College football | $1,195,007 | 100% | +$26,801 (+2.2%) | -1.03% | +2.85% | -0.99% |
| NFL | $787,217 | 100% | -$3,101 (-0.4%) | +1.22% | +1.80% | -0.70% |
| Premier League | $620,860 | 99% | +$3,523 (+0.6%) | +3.11% | +1.43% | -1.03% |
| LaLiga | $563,358 | 93% | -$15,825 (-2.8%) | -0.28% | +1.97% | -0.11% |
| ATP | $299,869 | 100% | +$4,250 (+2.0%) | +0.25% | +1.87% | -0.35% |
| NBA | $299,511 | 56% | -$1,819 (-0.7%) | +1.11% | +4.69% | -1.29% |
| Serie A | $281,209 | 100% | +$25,070 (+8.9%) | -2.56% | +1.99% | +0.17% |
| Ligue 1 | $190,240 | 98% | +$27,314 (+14.4%) | +4.31% | +1.35% | -0.19% |
| Bundesliga | $179,981 | 100% | -$6,841 (-3.8%) | n/a | | |
| Brasileirão | $139,478 | 99% | -$16,043 (-13.1%) | n/a | | |

By market type, resolved maker: CFB spreads +14.0% ($467K) but totals -23.2% ($177K); EPL winner +3.6% ($358K); NBA spreads +4.7% ($88K), totals -4.7% ($103K). Markouts are print-based (last print on the same token) over the 8 largest markets per league only.
**Reading:** in every sport RN1's bids fill 1.4-4.7% under the last print and give back 0.1-1.3% in the first minute: the same engine everywhere. Both resolved P&L and 10-min markout are positive for Premier League, Ligue 1 and ATP. Both are mixed for CFB, NFL, NBA and Serie A, and both negative for LaLiga. Three days to result is far too noisy to rank leagues. Book-based markouts over weeks are needed.

## F. RN1 profit per month, 30 days to 24 Nov about 09:45Z (added 09:47Z, Nick 09:42Z: "you can easily work out what RN1 is making per month")
Source: data-api **/v2/positions** for the wallet (status CLOSED and OPEN, sort_by=TIMESTAMP, cursor paging; every row is asserted to be the wallet). 93,500 positions, de-duplicated by token. P&L = total_pnl (realised plus resolved/unrealised) per token, dated by last_event_at. Buy $ = avg_price x total_size. Scripts: monthly_pull.py and monthly_an.py. **This is before maker rebates and liquidity rewards, which are paid separately.**
- **All markets, last 30 days: +$274,637 on $61.1M bought = +0.45%** (37,002 markets; 17 of 31 days positive). Prior 30 days: +$524,462 on $66.7M (+0.79%).
- Polymarket's own leaderboard for the wallet (/v2/leaderboard, time_period=month; the param is honoured, a bogus value errors) gives **+$396,512 on $129.4M volume**, sports alone +$253,081. The gap to my +$275K is not reconciled. Likely causes are a different window, a different volume definition (about 2x mine), and rebates. UNVERIFIED.
- **NBA (slug nba-), last 30 days: +$7,672 on $4.11M bought = +0.19%, about $256/day.** 17 of 30 days positive. Daily range -$28,523 (22 Nov) to +$26,493 (17 Nov). The month total is far smaller than single-day swings, so NBA is not shown positive.
- Maker vs taker: the positions endpoint has no maker/taker split. The 3-day trade pull (section E) had NBA at 56% maker. A full 30-day split needs a trade pull per market (7,227 NBA markets); not done.
- By sport, last 30 days: cs2 +$163K (+3.6%), Serie A (slug sea; CORRECTION 10:06Z: earlier mislabelled "Saudi league") +$114K (+4.0%), nfl +$55K (+1.0%), Ligue 1 +$40K (+4.0%), cfb +$34K (+0.6%), Bundesliga +$14K, nba +$8K, LaLiga +$7K; epl -$120K (-4.3%), ucl -$46K, wta -$56K, atp -$180K (-1.9%).

## G. Probe: CS2, Serie A (slug sea, earlier mislabelled Saudi), Ligue 1 (added 10:00Z, Nick 09:55-09:56Z: "probe on CS2, Ligue 1 and the Saudi League first. Not full recordings"; "he could simply be using GRID")
**Method.**
- Markets: RN1's 25 largest markets per league over the last 30 days, from section F positions. Coverage is CS2 34%, Serie A 28% and Ligue 1 41% of his $ in each.
- Pull: data-api /v2/trades by condition_id, with every row asserted to that market (R-080). RN1 rows use user= with taker_only=false and true; the maker/taker split is the set difference. The market tape uses taker_only=true.
- P&L is to the result, from position final prices, before rebates.
- "vs print" = his fill price against the last earlier print by anyone, in outcome-0 terms, signed so positive is in his favour.
- Markout = the price move after his fill, in his favour, at 10 s, 30 s, 60 s and 300 s.
- "pre 30 s" = the move in his direction in the 30 s BEFORE his fill.
- No new recorders. Books are NOT available in the cloud: the CS2 book recorder is on Prime. So "price vs book" here is price vs last print. Scripts: probe_pull.py and probe_an.py; output in probe_result.json.

| | maker share | maker $ / P&L | taker $ / P&L | maker vs print | maker markout 30 s / 60 s / 300 s | taker pre 30 s | taker markout 30 s / 60 s / 300 s |
|---|---|---|---|---|---|---|---|
| CS2 | 75% | $1.13M / +$67.7K (+6.0%) | $380K / -$36.5K (-9.6%) | +0.86c | +0.46 / +0.45 / -0.17c | +0.61c | +1.61 / +2.03 / -0.28c |
| Serie A (sea) | 96% | $750K / +$42.2K (+5.6%) | $36K / +$1.0K (+2.9%) | +0.86c | +0.31 / +0.60 / +0.46c | +0.92c | +5.55 / +4.38 / +4.92c (36 fills) |
| Ligue 1 | 86% | $358K / -$16.5K (-4.6%) | $57K / -$5.1K (-9.0%) | +0.40c | +0.20 / +0.09 / +0.52c | +2.01c | -1.21 / -1.32 / -2.56c (43 fills) |

**Reading.**
- **CS2:** the profit is the maker side: resting bids that fill about 0.9c under the last print and are not picked off (small positive markout). His taker fills move in his favour for about 60 s (+2.0c) and then fade (-0.3c by 300 s), and they lose 9.6% to the result. They follow a move already under way (+0.6c in the 30 s before).
  - That is fast reaction, but it is not the source of his money. A GRID-style data edge would show up as taker profit; here the taker side loses.
  - We have no public-feed timestamps for these matches, so "30 s ahead of any feed" cannot be tested on his fills here. Our own PandaScore test (reviewer/pandascore/RESULT-inround-sign-placebo-10matches-2026-11-20.md, 15 matches, UNCHECKED) found the Polymarket price already moving about 1c in the 15 s BEFORE PandaScore's round-end message. So the market as a whole leads that public feed.
- **Serie A (sea; NOT Saudi):** almost pure maker, +5.6%, with resting quotes and no adverse selection. That is a copyable-rule candidate.
- **Ligue 1:** in his top 25 markets the maker side LOST 4.6%. Yet section F has the whole league at +4.0% and section E's 3 days at +14.4%. So the gain comes from his smaller markets, or it is noise.

## H. Probe round 2: ALL markets, CS2 / Serie A / Ligue 1 (added 10:11Z, Nick 10:04Z "keep probing until we find something concrete")
**Method.**
- Every RN1 market in the three leagues over the last 30 days: CS2 330 markets (73 matches), Serie A 1,060 (45 matches), Ligue 1 549 (34 matches). Coverage is 100% of his $.
- Pull: /v2/trades by condition_id, asserted per row. Maker/taker by the taker_only set difference. Kickoff from gamma gameStartTime (1,939 of 1,939 found). Market tape for the top 80 markets per league (CS2 70%, Serie A 56%, Ligue 1 72% of $).
- Uncertainty: a bootstrap over MATCHES, since markets in one match are correlated. P&L is to the result, before rebates.
- Scripts: probe2_pull.py, probe2_an.py, probe2_boot.py; outputs probe2_result.json, bootstrap.json, probe_result_top80.json.
- Section G's top-25 figures are superseded.

| | maker P&L (95% CI over matches) | matches maker+ | maker ex best 5 markets | taker P&L (95% CI) | taker markout 30 s / 60 s / 300 s (fills) |
|---|---|---|---|---|---|
| CS2 | +$70.4K on $3.54M, +2.0% (-$119K to +$275K) | 49% | -$23.6K | +$115.0K on $956K, +12.0% (-$45K to +$287K) | +2.31 / +2.51 / +2.77c (1,254) |
| Serie A | +$101.0K on $2.69M, +3.8% (-$30K to +$268K) | 47% | -$3.7K | +$15.8K on $151K (-$10K to +$47K) | +2.76 / +2.28 / +1.98c (101) |
| Ligue 1 | +$41.2K on $925K, +4.5% (-$37K to +$131K) | 47% | -$7.8K | -$0.5K on $81K | +0.17 / +0.17 / -0.82c (75) |

**Findings.**
1. **No copyable maker rule in any of the three leagues.** Maker P&L to the result has a 95% interval spanning zero everywhere. Fewer than half of matches are positive. Without the 5 best markets the maker side is negative in all three. The +4% is a handful of big results.
   - Timing, market type and price band don't rescue it: every positive cell is driven by one or two matches. Examples: the Serie A maker 0-10 min pre-kickoff cell, +$60.8K on $48K; Serie A spreads, +$46.3K on $91K.
   - Maker fills are small: median $22-46, 90th percentile $450-875.
2. **CS2 taker: the concrete signal.** After RN1 takes liquidity in CS2, the price keeps moving his way: +2.3c at 30 s, +2.5c at 60 s and +2.8c at 5 min, over 1,254 taker fills in 80 markets. The 30 s before his take moved only +1.0c.
   - That is well above the 0.75c fee at p 0.5 (0.03 x p(1-p)) and the 1 s sports delay. To the result it is +12.0% (+$115K on $956K), but with only 73 matches the interval spans zero (-$45K to +$287K). The top 20 taker fills make +$118K.
   - This is the signature of **faster in-game information**: a data edge such as GRID or a faster stream. It is not a rule we can copy from public data.
   - It matches our own PandaScore finding: Polymarket moves before the public round-end message.
3. **What would settle CS2:** time his taker fills against public event times (PandaScore kills and round ends) for the same matches. If his takes land before the public event, that confirms a feed faster than public. Our PandaScore capture (P118) is not running (PK P-PS-039). The read-only CS2 book extract (IT P140) will give the spread and depth at his fills.
