# Literature step-back: in-play betting and timing leads (7 Nov 2026)

**Confidence: 7/10.** Updated 7 Nov after Nick allowed arxiv.org, doi.org and econpapers.repec.org. I re-read the abstracts (not the full texts) of every arXiv paper below plus Bizzozero et al., Brown and the Croxson-Reade record, and corrected three errors from the first draft. Still **(unverified)**: the Croxson-Reade result, Angelini et al., Albers et al., Indriawan et al., Hodge et al., Dumitrescu et al., Dias, Gill et al., and the "60%" figure (from a working-paper abstract seen in a search snippet).

## Do we agree with Nick's framing?

Mostly yes. What we are trying to do is "latency trading in an in-play betting market": a faster information source (TheSports) against a slower price. That is exactly the "courtsiding" setting in the literature. Two differences. (1) Polymarket is an order book with no in-play bet delay that I know of, so the lead is only worth something if our orders land before the book moves. (2) We hold to resolution, so we are not trying to trade out. Almost none of the academic work is about esports, and almost none is about Polymarket yet.

## 1. Latency / information-lead trading

| Paper | Finding | What it means for us |
|---|---|---|
| Bizzozero, Flepp, Franck, "The effect of fast trading on price discovery and efficiency: evidence from a betting exchange", J. Econ. Behavior & Org. 2018. [DOI](https://doi.org/10.1016/j.jebo.2018.09.020) | Courtsiders (live at the tennis court) beat TV-delayed bettors. A simple strategy earned positive returns after big events. The working-paper version said the first few seconds of fast trading capture over 60% of the full price reaction. | Closest match to us. Support for "a lead of a few seconds is worth real money in tennis". It also says the money is in the first seconds, so our 2-3 s feed matters. |
| Brown, "Information acquisition in ostensibly efficient markets", Economica 2015. [EconPapers](https://econpapers.repec.org/article/blaeconom/v_3a82_3ay_3a2015_3ai_3a327_3ap_3a420-447.htm) | Wimbledon exchange data. Risk-free arbitrage appears often during matches as information arrives and shifts prices unevenly, and rarely before matches. | In-play prices are briefly inconsistent. Cheap to look for crossed or lagged prices. |
| Croxson and Reade, "Information and efficiency: goal arrival in soccer betting", Economic Journal 2014. [Reading](https://centaur.reading.ac.uk/34884) | Uses goals just before half-time as clean news. I only saw the setup, not the result. A secondary source says prices adjust almost instantly to public news **(unverified)**. | Warns that once news is public the price moves fast. The edge is only the seconds before that. |
| Angelini, De Angelis, Singleton, "Informational efficiency and behaviour within in-play prediction markets", Int. J. Forecasting 2022. [PDF](https://reading-9.eprints-hosting.org/98329/1/information_efficiency_angelini_de_angelis_singleton.pdf) | Football exchange data. Found some mispricing after the first goal, linked to favourite bias. | After-event mispricing can persist beyond seconds in some markets. Worth checking whether it does in ours. |
| Winkelmann and Deutscher, "Do betting markets sense a goal coming?", arXiv 2505.21275, May 2025. [arXiv](https://arxiv.org/abs/2505.21275) | No sign that the market anticipates the first goal. | The price does not lead the event. So any lead has to come from the feed, which fits what we are measuring. |

## 2. Execution: taker vs resting orders, adverse selection

| Paper | Finding | What it means for us |
|---|---|---|
| Lehalle and Mounjid, "Limit order strategic placement with adverse selection risk and the role of latency", arXiv 1610.00261. [arXiv](https://arxiv.org/abs/1610.00261) | Optimal placement of one limit order. Latency erodes the benefit of the control, so being fast reduces adverse selection. | Matches what Nick spotted on 7 Nov: a resting bid below market fills mostly when the signal is wrong. Strong reason to test taker and bid-at-the-current-price variants before the market-2.5% rule. |
| Albers et al., latency and taker adverse selection (Oxford ORA, link from search: [ORA](https://ora.ox.ac.uk/objects/uuid:cdab1de2-7576-42e2-abae-ab12371eba76/files/rs4655j600)). Title and year not verified. | Orders that would have done well without latency do worse with it. | Our measured order speed (ack about 0.2 s median, p90 1.3 s) is the number to put into any taker backtest. |
| Indriawan, Pascual, Shkilko, "On the effects of continuous trading" (working paper, not on arXiv as far as I saw). | Latency arbitrage raises the adverse-selection cost for people who post quotes. | Same message as above: if we post, a faster informed trader picks us off. |

## 3. Polymarket and prediction-market work (2026 preprints; abstracts read 7 Nov)

- Moshrefi, "Prices, Probabilities, and Parlays: Systematic Bias in Sports Prediction Markets", arXiv [2607.14430](https://arxiv.org/abs/2607.14430), July 2026. **Kalshi, not Polymarket**, 23 million moneyline trades. Calibration is perfect in the middle of a contract's life and breaks down in the final ten minutes before settlement; cross-game parlays are overpriced. Means: do not expect a general mid-game mispricing, so any edge has to come from the feed. Avoid trading near the end.
- Cheng, Yang, Zou, "Arbitrage Analysis in Polymarket NBA Markets", arXiv [2605.00864](https://arxiv.org/abs/2605.00864), April 2026. 75 million order-book snapshots, 173 games. Single-market anomalies are very rare: 7 executable in-game episodes with a median length of 3.6 seconds. Combinatorial gaps are more frequent, concentrated in the final minutes, and execution is limited by shallow books. Means: the book is efficient against simple arbitrage, so our test is the feed lead and not stale quotes. Size will be capped by depth.
- Qin and Yang, "Polymarket-v1 Database", arXiv [2606.04217](https://arxiv.org/abs/2606.04217), June 2026. 1.2 billion on-chain trades, 2022-2026, with true aggressor direction. Says market making is concentrated. Means: a usable source for who takes versus rests in backtests.

## 4. Win-probability models

- **Tennis:** Klaassen and Magnus point-by-point Markov model, and Dumitrescu et al. (Imperial), who show the score can be recovered from exchange odds ([PDF](https://www.doc.ic.ac.uk/~wjk/publications/DumitrescuHuangKnottenbeltSpaniasWozniak.pdf)). Means: a simple "probability each player wins a point, then dynamic programming" model is the textbook baseline and is cheap to build. The 2026 arXiv preprint "Forecasting the Winner of a Live Tennis Match" (Xie and Muppidi, [2609.07617](https://arxiv.org/abs/2609.07617)) reports 76% / 82% / 88% accuracy at 25% / 50% / 75% of the match on 8,222 Grand Slam matches, but the authors look like students, so treat it as weak.
- **Esports:** Hodge et al., live win prediction for Dota 2 and CS:GO, IEEE Trans. on Games 2021 (up to about 85% accurate after 5 minutes; [White Rose](https://eprints.whiterose.ac.uk/152931/)). I found no arXiv paper on live LoL win probability; arXiv [2609.08060](https://arxiv.org/abs/2609.08060) is pre-game only. Means: our own event-jump models are ahead of the literature here. Do not wait for a paper.
- **NBA:** Dias 2016 thesis (4 NBA Finals games, in-play odds not efficient, tiny sample; [PDF](https://repositorio.iscte-iul.pt/bitstream/10071/13473/1/AndreDias_tese.pdf)) and Gill et al. 2003 (score and time left dominate in-game prices; [PDF](https://clgiles.ist.psu.edu:443/papers/ACM-2003-Sports-Betting.pdf)). Means: score difference and time remaining is a fine first model. Not worth more.
- **Courtsiding background (not academic):** [FiveThirtyEight](https://fivethirtyeight.com/features/inside-the-shadowy-world-of-high-speed-tennis-betting) and the UK Gambling Commission ([in-play betting](https://www.gamblingcommission.gov.uk/licensees-and-businesses/guide/in-play-or-in-running-betting)) both say operators buy fast score feeds and use bet delays. That is why the lead is shrinking and why unofficial feeds are a cat-and-mouse game.

## What the literature does not tell us

- Nothing measures a feed lead on Polymarket or in esports. Our own TheSports data is the only evidence.
- No paper gives a verified rule for taker vs resting orders in betting markets. The order-book papers above are equities-style theory.
- Prices adjust within seconds to about a minute after a clean event, so we should expect the lead to be worth a few seconds at most.

## The "dumbest" strategies to test first (paper only, all held to resolution)

Each one uses only the feed event and the market. No win model.

1. **Follow the feed, taker:** the moment the feed reports an event, take the ask on the side that should rise, only if the price has not yet moved. Hold. This is the cleanest test of "is there a lead" and the one the courtsiding paper implies.
2. **Same but only on events where the feed was first:** skip any event where the book had already moved. Matches Nick's "judge on events where the feed leads, not the median".
3. **Bid at the pre-event best bid, cancel after N seconds** (already in progress). The Lehalle-Mounjid logic says fills here are adverse, so compare fills and P&L against variant 1.
4. **Placebo:** same entries as variant 1 but on the wrong side, and on random timestamps. If the placebo loses about the spread, we are measuring cost correctly.
5. **Fixed-size, fixed-price-cap:** buy only if the ask is within 1-2 cents of the pre-event mid. Removes any model and caps the cost of being late.
6. **Score-state fair value, no feed lead:** simple tennis Markov or NBA score-and-time model against the price, trade only when the gap beats spread plus fee. The literature says this should do nothing mid-game; it is a useful negative control.
7. **Skip the last minutes and the extremes** (calibration paper): a filter to test on top of 1.

Next step: run 1, 2 and 4 on the TheSports capture per sport, with the 0.2 s / 1.3 s order delay, and report fills, move left after our order, and P&L per event with a confidence interval.

## Full-text read, 7 Nov 04:40Z: what the numbers say and what this means for our algo

Read in full: Cheng, Yang, Zou (arXiv 2605.00864) and Lehalle and Mounjid (arXiv 1610.00261, v4). **Not read in full:** Bizzozero et al. (Elsevier) and Brown 2015 (Wiley / UEA working paper). Their hosts (linkinghub.elsevier.com, onlinelibrary.wiley.com, ueaeco.github.io, hal.science) are blocked, so I only have their abstracts. Their edge-duration and return numbers are therefore still missing.

**Cheng, Yang, Zou (Polymarket NBA, 173 games, 4 Feb-4 Mar 2026)**
- Data: Polymarket CLOB `/book` top-of-book snapshots, polled every 3.6 to 5.5 s. They cannot see anything shorter than about 4 s.
- Single-market arbitrage (Yes+No under $1, or over $1 by minting): only 7 executable in-game episodes in 75 million snapshots. Median 3.6 s, which is just their polling interval. Capped profit $210 on $100 per episode, median yield 11%.
- Combinatorial (moneyline vs spread): 290 episodes, median 16 s in-game, 17% lasted 4 s or less, mostly in the final minutes. Median return 101 bps, but only 14.8 shares fit on average and 77% of episodes were depth-limited.
- Median bid-ask spread: 392 bps pre-game, 1,031 bps in-game, 7,533 bps after the game. This covers all NBA market types, so moneyline alone may be tighter. We should read the number from our own books.
- Authors' reading: market makers "occasionally require a few seconds" to reprice after a live shock.

**Lehalle and Mounjid (large-tick equities, AstraZeneca)**
- Theory plus a small data study. Latency is measured in order-book events, not seconds, so there is no clock-time number to borrow. Findings: a resting buy order is filled mostly when the price is about to fall; the value of cancelling and reposting on a signal shrinks as latency grows, faster for participants more exposed to adverse selection.

**What this means for our algo**
1. **The window is seconds, not tens of seconds.** The only direct Polymarket NBA evidence says dislocations close in about 4 s, and the paper cannot see below that. Our TheSports lead (2-3 s in places) sits inside the part nobody has measured. So the first test is timing at second resolution on our own captures, not new theory.
2. **A taker pays a lot of spread.** If in-game spreads are anywhere near 10%, a taker entry has to beat that on its own. This is why the taker variant should only fire when the move left is clearly bigger than the spread we see at that moment, and why the bid-at-current-price test (variant 3) matters.
3. **Resting orders fill when we are wrong.** Lehalle and Mounjid give the mechanism behind Nick's 7 Nov point. The fix they point to is fast cancel on a signal. Our measured cancel is about 0.13 s, so the cancel-after-N-seconds test is worth running with N of a few seconds.
4. **Depth caps size.** 14.8 shares average executable size in the arbitrage cases. Treat any backtest size above that scale as unproven.
5. **Book is efficient against simple arbitrage.** Do not spend time on Yes+No or moneyline-vs-spread arbitrage. The edge, if any, is the feed.

Strategy order is unchanged: take-on-feed (1) and feed-first-only (2) with the placebo (4) first, measured at second resolution.

## Refocus, 7 Nov 04:45Z: tennis and esports only (Nick: NBA is a waste of time)

NBA is dropped from here on. Everything above on NBA stays in the note only as background.

**Tennis (the best-covered case)**
| Paper | Finding | Meaning for us |
|---|---|---|
| Bizzozero, Flepp, Franck 2018 ([DOI](https://doi.org/10.1016/j.jebo.2018.09.020); abstract read, full text blocked) | Courtsiders' fast trades move prices to the right level quickly, and a simple strategy earned positive returns after important events. | Direct precedent for a feed that is seconds ahead. Numbers on seconds and returns still missing. |
| Easton and Uylangco, "Forecasting outcomes in tennis matches using within-match betting markets", Int. J. Forecasting 2010 ([EconPapers](https://econpapers.repec.org/RePEc:eee:intfor:v:26:y::i:3:p:564-575)). **Unverified: from a search summary only.** | Odds underreact to service breaks: the extra points a broken player tends to lose are not fully priced right away. No bias after a hold. | A second edge that needs no speed. Test: after a break, does the price keep drifting for tens of seconds? |
| Brown 2015 ([EconPapers](https://econpapers.repec.org/article/blaeconom/v_3a82_3ay_3a2015_3ai_3a327_3ap_3a420-447.htm); abstract only) | Wimbledon exchange arbitrage is frequent in-play, rare pre-match. | In-play tennis prices are briefly inconsistent. |
| Klaassen and Magnus point-by-point model; Dumitrescu et al. ([PDF](https://www.doc.ic.ac.uk/~wjk/publications/DumitrescuHuangKnottenbeltSpaniasWozniak.pdf)); Xie and Muppidi, arXiv [2609.07617](https://arxiv.org/abs/2609.07617) (abstract read; weak source) | Win probability from point-win rates by dynamic programming. Betting odds track these models closely. | A cheap fair-value model: how far a point or game should move the price. |

**Esports (almost nothing on prices)**
| Paper | Finding | Meaning for us |
|---|---|---|
| Yang, Qin, Lei, "Real-time eSports match result prediction", arXiv [1701.03162](https://arxiv.org/abs/1701.03162) (abstract read) | Dota 2: pre-match features 71% accurate; adding per-minute in-game features reaches up to 93.7% at minute 40. | Minute-level state is highly predictive but this is slow-moving. Event-level jumps (our approach) are not in the paper. |
| Xenopoulos, Coelho, Silva, arXiv [2109.12990](https://arxiv.org/abs/2109.12990) (abstract read) | CS:GO win probability at the start of each round from score, equipment and money. | A ready recipe for the size of a CS2 round-win move. |
| Hodge et al., IEEE Trans. on Games 2021 ([White Rose](https://eprints.whiterose.ac.uk/152931/); not re-read) | Live Dota 2 and CS:GO win prediction, up to about 85% accurate after 5 minutes. | Same point: state models exist, price-vs-event timing does not. |
| JIFS 2024, 46(3):7413 ([DOI](https://doi.org/10.3233/JIFS-232932); search summary only) and Sweeney 2021, Games and Culture (summary only) | Favourite-longshot biases in LoL, CS:GO, Dota 2 vary by title and tournament. | Pre-game bias, not in-play. Not our edge. |

**Gap:** I found no paper that measures an in-play price against an event feed in LoL, CS2 or Dota. Our TheSports capture is the evidence, and the literature gives method, not results.

**Dumbest tests, restricted to these sports (paper only, held to resolution)**
1. **Tennis, take-on-point:** when TheSports reports a game won or a break, take the ask on that player if the price hasn't moved. Placebo: same on a random side.
2. **Tennis, post-break drift (no speed needed):** buy the player who just broke at the market after 10-60 s and hold. If this works, the edge doesn't depend on the feed.
3. **CS2, take-on-round-win:** on the feed's round result, take the ask on the winner if the price hasn't moved; compare to the Xenopoulos-style round model for size.
4. **LoL / Dota, take-on-big-event only:** use our own jump table and trade only the events with the largest typical move, skip small ones.
5. **Feed-first-only filter on all four.** Count only events where the feed beat the book. Report separately.
6. **Bid at the pre-event best bid, cancel after N seconds** as the comparison for fills (already running).

## Brown 2015 read in full (UEA working paper, Nov 2013 version) and a finding that changes the taker test, 7 Nov 05:00Z

**Brown (Wimbledon men's singles, Betfair, 2008-2012, 68 matches, prices sampled every second)**
- Set-up: arbitrage between the match-winner market and the set-score markets. Risk-free once all four bets are filled.
- In-play there were 2,170 separate opportunities vs 534 pre-match (2% commission), though most sampled hours were pre-match.
- Duration: **in-play median 4-8 s, mostly 5 s; pre-match median up to 133 s.** The 5 s is not an accident: see below.
- Return per opportunity (2% commission, % of collateral): in-play median 0.2-0.6% for the first strategy and 0.6-2.0% for the second; pre-match medians mostly 0.04-0.65%. Maxima reach 14% and 68%. The paper itself notes the highest returns may arise in the first 5 seconds of an opportunity.
- Execution: Betfair applies a **5-second cooling-off period to every in-play bet**. The paper says its aim is to remove any advantage from seeing the action earlier (in the stadium or on a faster TV feed): it lets liquidity providers cancel before a market order matches. So the fastest an automated arbitrageur can complete four bets is 5 s.

**Why this matters for us (checked against Polymarket's own docs and API)**
- Polymarket has the same device. Its order-lifecycle docs (`polymarket-docs/pages/concepts__order-lifecycle.md`) describe a "sports/game delay": marketable orders on configured markets wait for a delay window before matching, status `delayed`.
- The CLOB market record has a `seconds_delay` field. On 7 Nov I read it for a sample of sports markets: **1 second on the tennis and Dota 2 / CS2 game markets I sampled, 0 on futures and props.** Those samples were older, unresolved listings, so the number at match time may differ. We must read it live per market.
- Consequence: a taker entry on the feed (tests 1-3 above) sits in a delay window during which market makers can cancel. Courtsiding's edge is exactly what this rule is built to neutralise. The taker test must (a) include the market's `seconds_delay`, (b) count a miss when the quote is cancelled in that window, and (c) use the measured order timings, not an assumed instant fill.
- It also means resting orders (post-only) are not subject to the delay. That does not make them safe, because of the adverse-selection result above, but the comparison of taker and resting variants must be done with the delay in place.

## Courtsiding paper read in full (7 Nov 05:10Z, via TinyFish)

Bizzozero, Flepp, Franck, "Insider trading and price efficiency: evidence from a betting exchange", University of Zurich working paper 368, Sept 2017 ([PDF](http://repec.business.uzh.ch/RePEc/zrh/wpaper/368_IBW_full_alt.pdf)). This is the working-paper version. The published JEBO 2018 version is "The effect of fast trading on price discovery and efficiency" and may differ. We could not open ZORA directly because of its anti-bot page, but TinyFish found and read this copy on another host.

**Data:** 141 Grand Slam men's singles matches (French Open and Wimbledon, 2009-2014), Betfair best back/lay odds for every second (1.3 million seconds), IBM point-by-point data. 365 set-won events and 79 tie-break events.

**Edge duration**
- The insider advantage is the delay of TV and score feeds, at least 5 s. They attribute the price move in the first 5 s after a set is won to courtsiders.
- Cumulative abnormal return after a set is won: **0.82% at 1 s, 3.06% at 5 s.** The first five seconds are **about 60% of the full price reaction** once the public sees it, and **about 80% for unanticipated events (tie-breaks).**
- Odds on average stabilise after about 10 s.
- Prices start moving before the public information is out, which is the evidence that fast traders exist.

**Execution method:** "sequential back-lay". Back the set winner at t=0, lay the same player 10 s later, locking in a profit whatever the result. The authors ignore the exchange's speed bump and assume market orders match immediately. They also ignore the 5% commission.

**Returns of the 10 s round trip**
| Events | Return | n |
|---|---|---|
| All set events | -0.87% (p=0.09) | 365 |
| All tie-breaks | -0.65% (p=0.69) | 79 |
| Balanced matches (set winner priced 25-75%), sets | +1.48% (p=0.15) | 97 |
| Balanced 25-75%, tie-breaks | +4.03% (p=0.03) | 29 |
| Strict balance 40-60%, sets | +2.96% (p=0.02) | 44 |
| Strict balance 40-60%, tie-breaks | +6.6% (p=0.11) | 12 |

Why negative overall, in the authors' words: when one player is a strong favourite the odds barely move, and when an underdog wins the odds are erratic because volume is low.

**What this adds for our algo**
1. **The lead is about 5 s and most of the move happens inside it.** That is 60-80% of the move in the first 5 s, not 100% after 10 s. Our TheSports lead (2-3 s on some events) is a bit under that. The shape of the answer matches ours: judge on events where we are first.
2. **Trade only balanced prices.** Without a filter the same rule loses money. With a 25-75% filter it is mildly positive, and with 40-60% it is clearly positive on 44 events. This is the cheapest filter to add to every test we run: skip events when the pre-event price is outside roughly 25-75%.
3. **Unexpected events carry the most.** Tie-breaks (unanticipated) gave the largest share (80%) and the largest returns. In our sports that points to break of serve, round wins when the score was close, and objectives that swing a map.
4. **Small samples.** The best cells are 12-44 events with p-values of 0.02-0.15. It is suggestive, not proven.
5. **It was a round trip, not hold-to-resolution.** Their trade sells after 10 s. Ours holds. The comparison should therefore also be run as 10 s exit versus hold on our data.
6. **It ignored the speed bump.** With a delay like Betfair's 5 s (Brown) or Polymarket's `seconds_delay`, the returns above are an upper bound for a taker.
