# Literature step-back: in-play betting and timing leads (7 Nov 2026)

**Confidence: 6/10.** Why not 9: arxiv.org, ideas.repec.org and the other paper hosts were blocked from this session, so I could not open any paper. Every finding below comes from search-result abstracts and snippets, not from reading the papers. Items marked **(unverified)** are second-hand. Fix: allow arxiv.org (and doi.org / econpapers.repec.org) in the session network settings and I will re-check each one against the abstract.

## Do we agree with Nick's framing?

Mostly yes. What we are trying to do is "latency trading in an in-play betting market": a faster information source (TheSports) against a slower price. That is exactly the "courtsiding" setting in the literature. Two differences. (1) Polymarket is an order book with no in-play bet delay that I know of, so the lead is only worth something if our orders land before the book moves. (2) We hold to resolution, so we are not trying to trade out. Almost none of the academic work is about esports, and almost none is about Polymarket yet.

## 1. Latency / information-lead trading

| Paper | Finding | What it means for us |
|---|---|---|
| Bizzozero, Flepp, Franck, "The effect of fast trading on price discovery and efficiency: evidence from a betting exchange", J. Econ. Behavior & Org. 2018. [DOI](https://doi.org/10.1016/j.jebo.2018.09.020) | Courtsiders (live at the tennis court) beat TV-delayed bettors. A simple strategy earned positive returns after big events. The working-paper version said the first few seconds of fast trading capture over 60% of the full price reaction. | Closest match to us. Support for "a lead of a few seconds is worth real money in tennis". It also says the money is in the first seconds, so our 2-3 s feed matters. |
| Brown, Economica 2015 (Wimbledon exchange data; exact title not verified, see [EconPapers](https://econpapers.repec.org/RePEc:bla:econom:v:82:y:2015:i:327:p:420-447)) | Risk-free arbitrage appears often during matches as prices update unevenly, and rarely before matches. | In-play prices are briefly inconsistent. Cheap to look for crossed or lagged prices. |
| Croxson and Reade, "Information and efficiency: goal arrival in soccer betting", Economic Journal 2014. [Reading](https://centaur.reading.ac.uk/34884) | Uses goals just before half-time as clean news. I only saw the setup, not the result. A secondary source says prices adjust almost instantly to public news **(unverified)**. | Warns that once news is public the price moves fast. The edge is only the seconds before that. |
| Angelini, De Angelis, Singleton, "Informational efficiency and behaviour within in-play prediction markets", Int. J. Forecasting 2022. [PDF](https://reading-9.eprints-hosting.org/98329/1/information_efficiency_angelini_de_angelis_singleton.pdf) | Football exchange data. Found some mispricing after the first goal, linked to favourite bias. | After-event mispricing can persist beyond seconds in some markets. Worth checking whether it does in ours. |
| Winkelmann and Deutscher, "Do betting markets sense a goal coming?", arXiv 2505.21275, May 2025. [arXiv](https://arxiv.org/abs/2505.21275) | No sign that the market anticipates the first goal. | The price does not lead the event. So any lead has to come from the feed, which fits what we are measuring. |

## 2. Execution: taker vs resting orders, adverse selection

| Paper | Finding | What it means for us |
|---|---|---|
| Lehalle and Mounjid, "Limit order strategic placement with adverse selection risk and the role of latency", arXiv 1610.00261. [arXiv](https://arxiv.org/abs/1610.00261) | Optimal placement of one limit order. Latency erodes the benefit of the control, so being fast reduces adverse selection. | Matches what Nick spotted on 7 Nov: a resting bid below market fills mostly when the signal is wrong. Strong reason to test taker and bid-at-the-current-price variants before the market-2.5% rule. |
| Albers et al., latency and taker adverse selection (Oxford ORA, link from search: [ORA](https://ora.ox.ac.uk/objects/uuid:cdab1de2-7576-42e2-abae-ab12371eba76/files/rs4655j600)). Title and year not verified. | Orders that would have done well without latency do worse with it. | Our measured order speed (ack about 0.2 s median, p90 1.3 s) is the number to put into any taker backtest. |
| Indriawan, Pascual, Shkilko, "On the effects of continuous trading" (working paper, not on arXiv as far as I saw). | Latency arbitrage raises the adverse-selection cost for people who post quotes. | Same message as above: if we post, a faster informed trader picks us off. |

## 3. Polymarket and prediction-market work (2026 preprints, all unverified)

- Prices, Probabilities, and Parlays: Systematic Bias in Sports Prediction Markets, arXiv [2607.14430](https://arxiv.org/abs/2607.14430). Snippet: contracts are worst calibrated long before the game and near the final whistle, and best calibrated during in-game play. Means: do not expect a general mispricing in mid-game; our edge has to be the feed, not a bias. Avoid trading near the end.
- Arbitrage Analysis in Polymarket NBA Markets, arXiv [2605.00864](https://arxiv.org/abs/2605.00864). Snippet: executable mispricings exist but are limited by liquidity and concentrated in the final minutes. Means: size will be capped by the book, consistent with our queue measurements.
- Polymarket-v1 Database, arXiv [2606.04217](https://arxiv.org/abs/2606.04217). Dataset paper; it cites a Yang and Tsang price-discovery study that I could not find. A possible data source for backtests.

## 4. Win-probability models

- **Tennis:** Klaassen and Magnus point-by-point Markov model, and Dumitrescu et al. (Imperial), who show the score can be recovered from exchange odds ([PDF](https://www.doc.ic.ac.uk/~wjk/publications/DumitrescuHuangKnottenbeltSpaniasWozniak.pdf)). Means: a simple "probability each player wins a point, then dynamic programming" model is the textbook baseline and is cheap to build. The arXiv 2026 preprint "Forecasting the Winner of a Live Tennis Match" ([2609.07617](https://arxiv.org/abs/2609.07617)) reports 76% / 82% / 88% accuracy at 25% / 50% / 75% of the match on 8,222 Grand Slam matches, but it is a student paper, so treat it as weak.
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
