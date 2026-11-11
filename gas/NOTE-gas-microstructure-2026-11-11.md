# How retail gas prices are set, and what moves the next AAA print (literature note, 11 Nov 2026)

Scope: reading only. No backtest, no model. Purpose: understand the microstructure before adding RBOB or other inputs to the Kalshi gas daily contracts (national and state, strikes 0.5c apart, AAA ~12:15Z print).
Confidence: 7/10 on the mechanisms and citations (read directly: Noel 2016 handbook chapter, Chesnes FTC paper, AAA/OPIS pages, abstracts for Lewis-Noel and Zimmerman et al.). 4/10 on "how big is a typical daily AAA move" because no source gave that number (see Gaps). arXiv is thin: it has only Kristoufek 2014 (arXiv 1407.5466, fractional integration, retail vs crude) and 2025 retail-price papers (arXiv 2512.02564) that touch the topic. The substance is in economics journals.

## 1. Supply chain and cost pass-through
- Cost chain: crude / RBOB futures / spot -> terminal rack (OPIS racks are posted ~9am, Mon-Sat) -> retail. Chesnes (FTC WP 302, Energy Journal 2016) finds the largest asymmetry in the rack-to-retail link, not crude-to-spot.
- Speed (Chesnes, 2000-2013 OPIS daily city data): full pass-through takes about two weeks. Example from the paper: a 10% wholesale rise gives a 10% retail rise after one week, but a 10% wholesale fall gives only about a 5% retail fall after one week and the full 10% after two weeks.
- Daily-data impulse responses: complete pass-through in 28 days after positive shocks and 17 days after negative shocks (footnote 32, with weekly data the order flips: 12 and 25). The paper's own two figures disagree, so treat day counts as +/- a week.
- Size of "rockets and feathers": about 2.45 cents per gallon on average (Chesnes), 2.3-2.6 cpg in earlier studies (Borenstein et al 1997; Balmaceda and Soruco 2008). The asymmetry sits in the first week; after that, up and down shocks look the same.
- Why it exists (Noel 2016 survey): consumer search is more intense when prices rise than when they fall (Lewis 2011; Lewis and Marvel 2011; Yang and Ye 2008; Tappata 2009; Cabral and Fishman 2012). Cities with more asymmetry also cycle more and pass through faster (Chesnes). Asymmetry is bigger for branded than unbranded stations.
- It is "not universal" and partly a measurement artefact (Noel 2016, citing Cook and Fosten 2019 "Replicating rockets and feathers").
- Stations also price off replacement cost, not just rack (Noel 2007 RESTAT), and sales-below-cost laws (for example Wisconsin 6% over cost) put a floor under margins.

## 2. Edgeworth price cycles (the part that creates day-to-day jumps)
- Mechanism (Maskin and Tirole 1988; Noel 2007, 2016 survey): stations undercut by small amounts each day until margins are thin, then one station raises price sharply (often 10-20%, typically on a similar day of week) and others follow within hours to days. The sawtooth happens even with flat costs.
- Where: in the US only a "relatively small number of MSAs in contiguous upper Midwestern states" cycle, and they started in 2000 (Zimmerman, Yun and Taylor 2013, RIO). Canada, Australia, Norway, Germany also cycle.
- Timing in the US: "most often weekly" (Noel 2016, citing Lewis 2009, Doyle et al 2010, Lewis and Noel 2011, Zimmerman et al 2013). Weekly cycles often restore on the same weekday (Noel 2018, "Calendar synchronization"). Typical amplitude 8-10% of price (Noel handbook chapter; mostly non-US evidence, so do not read this as a US national number).
- Speed: cost changes pass through 2-3 times faster in cycling markets (Lewis and Noel 2011, RESTAT 93(2)). Cycles also recover faster after supply shocks (Lewis 2009 Hurricane Rita).
- Cycling can look like extreme pass-through when a cost rise lands near a trough (Noel 2016: apparent pass-through "in the hundreds or thousands of percent"), while a cost fall just gives more room for undercutting.

## 3. How AAA's number is built
- Source: OPIS, using fleet-card (WEX) transaction data. AAA states "up to 120,000 stations" surveyed every day, based on credit card swipes (gasprices.aaa.com/about-aaa). OPIS says it captures up to 150,000 stations in North America.
- Chesnes on the OPIS retail series: prices are "(usually) end of the day prices as they are recorded from the last swipe of a consumer's fleet-card on a given day", averaged over at most one price per station per day (OPIS city averages).
- So the AAA print is a station-count-weighted (not volume-weighted, as far as the sources say) average of last-swipe prices from the previous day. The exact cut-off and the weighting are not published. Treat the ~12:15Z timing as the coordinator's input, not something this reading confirmed.
- Implication: day-to-day AAA change = (stations that changed their price since their last swipe) x (size of change). With about 120k stations, noise from sampling is small, so the daily change is almost all real price changes, and the mix of which stations swipe in a day adds a little noise.

## 4. What predicts tomorrow's AAA change (literature view, no numbers measured here)
1. Rack/RBOB change over the previous 1-3 days vs current retail margin. Margin is the gap between retail and rack. When margin is thin, retail moves up; when fat, it drifts down. Error-correction models in Chesnes use this directly.
2. Direction asymmetry: a rise in cost is passed on about twice as fast in the first week as a fall (Chesnes). So rises should show up faster and falls should be spread over about two weeks.
3. Cycle phase in cycling states (Midwest weekly cycles): restoration days produce the big one-day jumps and undercutting days produce small steady declines. This matters most for state contracts in OH, IN, MI, WI, KY, IL and less for the national average.
4. Persistence: past retail changes themselves carry forward because of slow pass-through (this is what the "AAA last change" momentum signal in our scan was capturing, and it did not beat the market).
5. Calendar/weekday effects: cycle restorations cluster on specific weekdays (Noel 2018). No source found for a US national weekday effect.
6. Shocks: hurricanes, refinery outages, tax changes (state excise changes are often passed through quickly and fully, but mixed results: Noel 2016).

## 5. Which drivers are observable before the Kalshi contract closes
Contract: open ~13-15h, settles on the ~12:15Z AAA print.
- Known in advance of close and of the print: rack prices (posted ~9am the previous day), RBOB/NYMEX futures through the close, retail margin proxy (AAA posted level vs RBOB-implied cost), previous AAA prints (including today's 12:15Z-ish print for the previous day's data), the AAA price history for cycle phase in each state, calendar (weekday), scheduled tax changes, weather/hurricane/outage news.
- NOT observable: the day's actual last-swipe prices that make up the print, intra-day station price changes (GasBuddy crowd data is a partial proxy, Atkinson 2009 finds it reliable on average but weak for independents), the OPIS-AAA exact cut-off.
- Practical reading: when the contract is traded, the information set is the cost move from yesterday's close onward plus where each state sits in its cycle. The final AAA value is mostly set by price changes that already happened the day before.

## 6. Gaps (what settles them, cheaply)
- Typical size of daily AAA national and state moves, the distribution of 0.5c strikes near the final, and how much of the variance is explained by yesterday's RBOB change: not in these papers. The AAA history (we already hold) gives the descriptive stats; no model needed.
- Noel and Chu (2015, Energy Economics 51), "Forecasting gasoline prices in the presence of Edgeworth price cycles", is the closest paper to the question. ScienceDirect blocked the fetch; only the citation and the Lewis-Noel snippet were read. Next step is an open copy or a paper that cites it.
- Kahl and Wein (JIE 2025, "How to reach the paradise?") on which station moves first in a cycle: read only the title and abstract snippet.

## Sources
- Noel, M. (2016) "Retail gasoline markets", Handbook on the Economics of Retailing and Distribution; https://www.noeleconomics.com/articles/NOEL_EER_gasoline.pdf
- Chesnes, M. (2016) "Asymmetric pass-through in US gasoline prices", Energy Journal 37(1); FTC WP 302; archived PDF via scholar.archive.org
- Lewis, M. and Noel, M. (2011) RESTAT 93(2) 672-682; abstract at ideas.repec.org/a/tpr/restat/v93y2011i2p672-682.html
- Zimmerman, Yun and Taylor (2013) RIO 42, 297-320, doi 10.1007/s11151-012-9372-6 (abstract only)
- Eckert (2013) "Empirical studies of gasoline retailing: a guide to the literature", J Economic Surveys (title and snippet only)
- AAA: https://gasprices.aaa.com/about-aaa/ ; OPIS retail pricing methodology PDF (2026)
- Kristoufek (2014) arXiv:1407.5466 (not read in detail)
