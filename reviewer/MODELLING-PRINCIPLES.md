# Modelling principles for testing edges in decision markets

Reviewer, 21 Nov 2026 (v2 04:50Z: corrections and three new sections from Nick's review at 04:04Z). Scope: any binary contract that settles on an observable outcome (crypto price windows, weather buckets, economic releases, events). Worked examples: MFW (BTC 5-minute Up/Down, nm792/mfw-clone) and Temperature (daily high/low buckets, nm792/trading-test). Companion files: `reviewer/TESTING-PRINCIPLES.md` and `TESTING-EVIDENCE.md` (mfw-clone reviewer 2069dd45), audit `reviewer/audit-2026-11-21/AUDIT.md` (a80a7052), Temperature `reviewer/temperature/OUTBOX.md` R-006, R-016, R-017, R-019, R-020 (trading-test reviewer).

This file is conceptual. It states what the maths says a test can and cannot tell us, and maps each principle to an error we made. It gives no strategy views and no trading instructions.

**For the reviewer of this file:** every principle cites primary work, and every citation was checked against a primary listing (Crossref, arXiv, NBER) on 21 Nov 2026; see section 17. Citations support principles only; no number in our results rests on them.

---

## 0. The one-paragraph version

We are running a decision problem (which rules get paper capital and attention) but have been using a hypothesis-testing tool (reject/accept at p95) as if it answered it. On our sample sizes the test has almost no power, so "not significant" mostly means "not measured", and a hard gate then throws away real edges at roughly the rate it keeps them. Separately, some of our models used information that was not available at the decision moment, which makes any result from them meaningless, positive or negative. The fix is: (1) make every input measurable at decision time, (2) cut the noise per decision before adding decisions (score against later market prices, not only settlement), (3) estimate edge with honest uncertainty and shrink it, (4) run forward tests sequentially with pre-set success and futility boundaries, so "dead" has a formal meaning, (5) correct for multiple testing in the estimate, not by deleting candidates, and (6) size every edge by fillable depth before calling it a business.

---

## 1. A test answers a different question from the one we are asking

**Principle.** Neyman-Pearson testing controls the long-run rate of false rejections of a null at a fixed level α; it says nothing about which action has higher expected value. Decision theory chooses the action that maximises expected utility given a loss function and current beliefs. When the costs of the two errors are asymmetric, the right threshold is set by those costs and by prior odds, not by α = 0.05.

- Neyman & Pearson (1933), "On the problem of the most efficient tests of statistical hypotheses", *Phil. Trans. R. Soc. A* 231:289-337. https://doi.org/10.1098/rsta.1933.0009 (V)
- Wasserstein & Lazar (2016), "The ASA Statement on p-Values: Context, Process, and Purpose", *The American Statistician* 70(2):129-133. Principle 3: "Scientific conclusions and business or policy decisions should not be based only on whether a p-value passes a specific threshold." https://doi.org/10.1080/00031305.2016.1154108 (V)
- Howard (1966), "Information Value Theory", *IEEE Trans. Systems Science and Cybernetics* 2(1):22-26: the value of more data is the expected improvement in the decision it buys. https://doi.org/10.1109/TSSC.1966.300074 (V)

**Asymmetry in our setting.** Discarding a real edge loses its whole future P&L stream (Nick's estimate for fast2: about $1m NPV). Paper-trading a false one costs some forward windows and attention, and is caught by its own forward record. The decision-theoretic threshold for "keep testing" is therefore far below the threshold for "commit real capital". We used one threshold (p95) for both.

**Our errors.** MFW nowcast taker s120-240: +$1,387 (p95.2) and +$1,060 (p94.2) on 100 forward windows, both halves positive, put on KNOWN-DEAD. PREREG-M1: +$135 (p92.9) put on KNOWN-DEAD. fast2: "0 of 144 passed" reported as a failure while 84 of 331 scored rows had P&L > 0 (TESTING-EVIDENCE rows 1-3). Each was a decision to stop collecting information, taken with a tool that does not price information.

---

## 2. Power: a test that cannot see the edge gives no verdict

**Principle.** Power is the probability a test detects an effect of a given size. With per-window noise σ and an effect μ measured as the distance from the null's mean, the windows needed at level α and power 1-β are about n ≈ ((z_{1-α} + z_{1-β}) σ / μ)². When n is far below that, a non-significant result is uninformative, and a significant one systematically overstates the effect (Type M error) and can get its sign wrong (Type S).

- Cohen (1992), "A power primer", *Psychological Bulletin* 112(1):155-159. https://doi.org/10.1037/0033-2909.112.1.155 (V)
- Button et al. (2013), "Power failure: why small sample size undermines the reliability of neuroscience", *Nature Reviews Neuroscience* 14:365-376: low power lowers the chance that a significant finding is true and inflates its size. https://doi.org/10.1038/nrn3475 (V)
- Gelman & Carlin (2014), "Beyond Power Calculations: Assessing Type S (Sign) and Type M (Magnitude) Errors", *Perspectives on Psychological Science* 9(6):641-651. https://doi.org/10.1177/1745691614551642 (V)
- Harvey & Liu (2020), "False (and Missed) Discoveries in Financial Economics", *Journal of Finance* 75(5):2503-2553; arXiv:2006.04269. Calibrates Type I and Type II errors together and shows standard multiple-testing hurdles lack power to detect skilled managers. https://arxiv.org/abs/2006.04269 (V)

**Our numbers.** Per-window null SD about $101 (nowcast e0.03), $86 (e0.05), $24 (M1), $106 (MFW) against target net edges of $2-5 (AUDIT B.2). Our null is centred at zero edge minus fees, so μ is net edge plus fees: for nowcast, $1.74 net (the $500/day goal) + $3.42 fees = $5.16, giving n = (2.486 × 101 / 5.16)² ≈ 2,370 windows at one-sided α = 0.05 and 80% power; we tested 100. 100 windows detect μ = 2.486 × 101 / 10 ≈ $25, i.e. about $22 net per window. M1: (2.486 × 24 / (1.74 + 2.45))² ≈ 200. These reproduce AUDIT B.2.

**The positive control proved it.** MFW's own October fills, a known profitable trader, cleared p95 in only 2 of 44 blocks of 100 windows (4.5%, the chance rate), while 30 of 44 blocks were profitable and the whole month sat at the 97.7th percentile (AUDIT B.1). A test that fails the known winner at the chance rate has no power at that sample size. Every "fail" it issued on our rules carried no information.

**Rule.** Before any run: state σ per window from data, the target edge, and the n needed. Run the harness on a planted known edge (positive control) and on a null; it must pass the first and not the second at the registered n. This is the same logic as simulation-based calibration of an inference pipeline: Talts et al. (2018), "Validating Bayesian Inference Algorithms with Simulation-Based Calibration", arXiv:1804.06788. https://arxiv.org/abs/1804.06788 (V)

---

## 3. Joint gates on correlated settings destroy power

**Principle.** Requiring every arm to pass (an intersection-union test) keeps the false-positive rate at α but loses power. For independent arms the joint power is the product of the arms' powers; for positively correlated arms it lies between that product and the power of the weakest arm. Either way it is never higher than the weakest arm's power, so an AND gate can only lose power relative to testing one pre-chosen arm. Rejecting a rule because one of two highly correlated parameter settings missed a bar by 0.8 percentiles is mostly noise.

- Berger (1982), "Multiparameter hypothesis testing and acceptance sampling", *Technometrics* 24(4):295-300 (intersection-union tests). https://doi.org/10.1080/00401706.1982.10487790 (V)

**Our error.** Nowcast prereg required e0.03 AND e0.05 to clear p95. e0.03 cleared (95.2), e0.05 hit 94.2, the rule was failed (TESTING-EVIDENCE row 5).

**Rule.** One rule, one estimate. If a family of settings is tested, model it jointly (section 5) or apply an explicit, stated split of α, never an AND.

---

## 4. Many weak edges: breadth beats a single strong signal

**Principle.** Grinold's fundamental law: information ratio ≈ IC × √breadth, where IC is the skill per independent bet and breadth the number of independent bets per period. A tiny per-bet edge across many independent bets compounds into a high Sharpe; the transfer coefficient (how much of the signal survives constraints) scales it down.

- Grinold (1989), "The Fundamental Law of Active Management", *Journal of Portfolio Management* 15(3):30-37. https://doi.org/10.3905/jpm.1989.409211 (V). Full text checked: Grinold writes the law as "SR = Mc²" (eq. 1, p. 30), where his SR is defined as the square of the information ratio (eq. 4), so IR = c√M with c = skill and M = breadth, the number of independent bets per year. It rests on three stated assumptions (p. 37): managers know their own skill and use it optimally, the sources are independent, and each has the same skill c.
- Clarke, de Silva & Thorley (2002), "Portfolio Constraints and the Fundamental Law of Active Management", *Financial Analysts Journal* 58(5):48-66 (transfer coefficient). https://doi.org/10.2469/faj.v58.n5.2468 (V)

**Implication for us.** BTC 5-minute markets give about 288 windows a day; weather gives many station × bucket × side × time cells a day. Edges of $1-5 per window are exactly the regime where breadth carries the result, and exactly the regime where a 100-window significance test is blind (section 2). A known profitable trader with ~1,000 markets/day is the illustration. The useful unit of evaluation is the portfolio of weak, roughly independent rules, not each rule's own t-stat.

**Breadth obeys the same square-root law as power.** Breadth does not make a weak edge fast to earn any more than it makes it fast to detect. Worked example: a $2 edge per window with $100 SD per window at 288 windows/day gives a daily mean of $576 and a daily SD of $100 × √288 ≈ $1,697, so a daily Sharpe of 0.34 (about 6.5 annualised). About 37% of days lose (P(Z < −0.34)), and confirming the edge at two standard errors takes (2/0.34)² ≈ 35 days. A good annual Sharpe and a slow, noisy daily record are the same fact. The lever that changes both is lower noise per decision (section 12), not more decisions alone.

**Caveat.** Breadth counts *independent* bets. Rules that fire on the same windows on the same signal are not independent; their correlation must be measured before their Sharpes are added.

---

## 5. Estimate and shrink; don't pass/fail

**Principle.** When many related cells are estimated at once, the raw estimate of each is dominated by noise, and the best-looking cells are biased upward (winner's curse). Partial pooling (empirical Bayes / hierarchical models) shrinks each cell toward its group mean in proportion to its noise. This gives better estimates of every cell than either treating them separately or pooling them all, and it handles multiple comparisons inside the estimate rather than by deleting cells.

- Efron & Morris (1975), "Data Analysis Using Stein's Estimator and its Generalizations", *JASA* 70(350):311-319. https://doi.org/10.1080/01621459.1975.10479864 (V)
- Efron (2011), "Tweedie's Formula and Selection Bias", *JASA* 106(496):1602-1614: corrects the selection bias of the top-ranked estimates. https://doi.org/10.1198/jasa.2011.tm11181 (V)
- Gelman, Hill & Yajima (2012), "Why We (Usually) Don't Have to Worry About Multiple Comparisons", *J. Research on Educational Effectiveness* 5(2):189-211; arXiv:0907.2478. https://arxiv.org/abs/0907.2478 (V)
- Andrews, Kitagawa & McCloskey (2024), "Inference on Winners", *QJE* 139(1):305-358; NBER WP 25456: valid confidence intervals and median-unbiased estimates for the cell chosen because it ranked first. https://www.nber.org/papers/w25456 (V)

**Our errors.** fast2 cells, nowcast arms and M1 were each judged alone against a bar, then binned as alive/dead. The right output is a posterior (or shrunk) edge per cell with an interval, grouped by mechanism (taker/maker, phase of window, fair-value source; for Temperature: leg × station × time-to-report × local hour). The ranked table at a80a7052 is the raw input to that, not the end product.

**How informative the current ranking is.** For cells with about $100 SD per window, 34 windows give a standard error of about $100/√34 ≈ $17 per window, against edges of $2-5. At that sample the ordering of the top band is mostly noise; shrinkage will pull most cells close to the group mean. The ranking is a starting allocation for forward testing (section 7), not evidence about which cell is best. Lower-noise cells (M1, about $24 SD) rank more reliably at the same sample.

**Rule.** Report shrunk edge, interval, and probability edge > cost for every cell. Rank on that. Nothing is deleted; a cell's rank moves as data arrives.

---

## 6. Multiple testing done properly, without overcorrecting

**Principle.** Searching over many rules inflates the best in-sample result. The literature gives three families of correction: (a) control the false discovery rate rather than the family-wise error rate, which keeps much more power; (b) test the best rule against a bootstrap of the whole search (reality check, SPA, stepwise); (c) deflate a reported Sharpe for the number of trials, non-normality and track length, or estimate the probability that the in-sample winner ranks below the median configuration out of sample. All of these adjust *confidence* in a ranking; none of them says to discard rules that miss, and Harvey & Liu (2020) show that current multiple-testing methods lack power to detect outperforming managers.

- Benjamini & Hochberg (1995), "Controlling the False Discovery Rate", *JRSS-B* 57(1):289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x (V)
- Storey (2002), "A direct approach to false discovery rates", *JRSS-B* 64(3):479-498. https://doi.org/10.1111/1467-9868.00346 (V)
- White (2000), "A Reality Check for Data Snooping", *Econometrica* 68(5):1097-1126. https://doi.org/10.1111/1468-0262.00152 (V)
- Hansen (2005), "A Test for Superior Predictive Ability", *J. Business & Economic Statistics* 23(4):365-380. https://doi.org/10.1198/073500105000000063 (V)
- Romano & Wolf (2005), "Stepwise Multiple Testing as Formalized Data Snooping", *Econometrica* 73(4):1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x (V)
- Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance", *Notices of the AMS* 61(5):458-471. SSRN 2308659. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659 (V)
- Bailey & López de Prado (2014), "The Deflated Sharpe Ratio", *J. Portfolio Management* 40(5):94-107. SSRN 2460551. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 (V)
- Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting", *Journal of Computational Finance* (online September 2016). https://doi.org/10.21314/jcf.2016.322 (V); preprint SSRN 2326253 (2013), https://doi.org/10.2139/ssrn.2326253 (V)
- Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns", *Review of Financial Studies* 29(1):5-68. https://doi.org/10.1093/rfs/hhv059 (V)
- Harvey & Liu (2020), above (V).

**Two-sided lesson for us.** Overfitting risk is real: 1,020 sequences × settings will produce lucky winners, and the top band's in-sample P&L is biased up (section 5). But the remedy is to *count the trials, deflate the estimate, and test forward*, not to raise the bar until a known profitable trader fails it. Our fast2 report ("0 of 144") applied a per-cell p95 bar with no FDR and no forward step, and read the outcome as a family verdict. That is overcorrection into false negatives.

**Rule.** Log the number of configurations tried per family (needed for deflation). Use FDR or a deflated Sharpe to rank confidence; use forward data to decide.

---

## 7. Forward testing a ranked band is a bandit problem

**Principle.** Choosing which of many candidate rules to paper-trade next, while learning which ones work, is an explore-exploit problem. Bandit algorithms allocate trials to arms in proportion to their probability of being best (Thompson sampling) or by optimistic bounds (UCB); best-arm and top-m identification variants aim to find the best arm or the best m arms with the fewest trials. The knowledge gradient allocates the next measurement where it most improves the final choice. All of them keep weak-looking arms in play until their own data rules them out.

- Thompson (1933), "On the likelihood that one unknown probability exceeds another in view of the evidence of two samples", *Biometrika* 25(3/4):285-294. https://doi.org/10.2307/2332286 (V)
- Auer, Cesa-Bianchi & Fischer (2002), "Finite-time Analysis of the Multiarmed Bandit Problem", *Machine Learning* 47:235-256. https://doi.org/10.1023/A:1013689704352 (V)
- Russo, Van Roy, Kazerouni, Osband & Wen (2018), "A Tutorial on Thompson Sampling", *Foundations and Trends in ML* 11(1); arXiv:1707.02038. https://arxiv.org/abs/1707.02038 (V)
- Russo (2020), "Simple Bayesian Algorithms for Best-Arm Identification", *Operations Research* 68(6):1625-1647. https://doi.org/10.1287/opre.2019.1911 (V); arXiv:1602.08448 (top-two Thompson sampling). https://arxiv.org/abs/1602.08448 (V)
- Kalyanakrishnan, Tewari, Auer & Stone (2012), "PAC Subset Selection in Stochastic Multi-armed Bandits", ICML 2012, pp. 655-662 (top-m identification, LUCB). https://mlanthology.org/icml/2012/kalyanakrishnan2012icml-pac/ (V)
- Frazier, Powell & Dayanik (2008), "A Knowledge-Gradient Policy for Sequential Information Collection", *SIAM J. Control Optim.* 47(5):2410-2439. https://doi.org/10.1137/070693424 (V)

**Paper trading is cheap to parallelise.** Unlike real capital, paper arms do not compete for money, only for compute and attention, so all of the band can run on the same live windows at once (this was done for 25 MFW cells at 03:01Z, AUDIT A). The bandit framing then governs (a) which cells get promoted to real-capital tests and (b) which new cells enter the band. When to stop observing a cell is a sequential-testing question (section 13).

**Our errors.** Testing one arm, waiting, then killing it; parking a prereg for "new windows" when recorded data existed (MEMORY hard rules, 20 Nov); treating ~900 never-run sequences as failed (TESTING-EVIDENCE row 7). In bandit terms an unpulled arm has its prior, not a loss.

---

## 8. No hindsight: decisions must be measurable on the information set at decision time

**Principle.** In stochastic-process language, information available up to time t is a filtration F_t. A trading strategy must be *predictable* (or adapted): the position taken at t may depend only on F_t (strictly, F_{t-}). Any quantity that depends on the future, including the *time* chosen for a decision, breaks this, and the backtest no longer describes a strategy anyone could run. The same applies to the model's training data: a model fitted at t may use only rows whose inputs and labels were known before t. In machine learning this is called leakage.

- Harrison & Pliska (1981), "Martingales and stochastic integrals in the theory of continuous trading", *Stochastic Processes and their Applications* 11(3):215-260 (trading strategies as predictable processes; p. 223: "Define a trading strategy to be a predictable vector process... Predictable means φ_t ∈ F_{t−1}... the portfolio φ_t must be established before, and held until after, announcement of the prices S_t"). https://doi.org/10.1016/0304-4149(81)90026-0 (V)
- Kaufman, Rosset, Perlich & Stitelman (2012), "Leakage in Data Mining: Formulation, Detection, and Avoidance", *ACM TKDD* 6(4):15. https://doi.org/10.1145/2382577.2382579 (V)
- Bergmeir & Benítez (2012), "On the use of cross-validation for time series predictor evaluation", *Information Sciences* 191:192-213 (recommends blocked cross-validation for time series; it found standard CV's theoretical flaws had no practical effect in its experiments, so it supports evaluation design, not the leakage rule itself). https://doi.org/10.1016/j.ins.2011.12.028 (V)

**Two concrete forms in our work.**
1. *Stopping-time leak.* Temperature decision time was set 5-30 minutes before the reading that set the day's extreme (us_l15_loader_nolgb.py:117, 95f164e5e). The time of the day's extreme is not a stopping time with respect to the live filtration; you only know it after the day. All results from it are INVALID (R-006). Fix: decide on a fixed grid (every 5 minutes) for every bucket, all legs (R-007).
2. *Training-set leak.* The grid model's error range was trained on residuals taken 15 minutes before each prior day's extreme (grid_layer.py:168-173, 6d27ad3c6), then applied at every scan time (R-017). The live state is clean but the predictive distribution is conditioned on an event (being 15 min before the extreme) that is not observable at scan time. Residuals near the extreme are small, so the model is overconfident early in the day, which is where live trading lost (R-020).

**Rule.** Code review starts by tracing, per leg, the time each decision is made and the timestamp of every input and every training row. Add a test that fails if any input or training row is located relative to an outcome-defined time (t_rep, extreme time, settlement price). A *book* read after the decision moment is also a leak (MEMORY pre-run gate).

---

## 9. Predictive distributions must be calibrated out of sample, conditioned the way they are used

**Principle.** A probabilistic forecast is judged by calibration (events forecast at p happen with frequency p; the probability integral transform, PIT, of outcomes is uniform) subject to sharpness (as concentrated as calibration allows), using strictly proper scoring rules (Brier, log, CRPS). Calibration must be checked out of sample and *conditional on every variable the decision uses*: a forecast calibrated on average can be badly miscalibrated by hour of day or season. In ensemble weather post-processing, the error model is estimated over a rolling training window, which trades off recency against sample size.

- Brier (1950), "Verification of forecasts expressed in terms of probability", *Monthly Weather Review* 78(1):1-3. https://journals.ametsoc.org/view/journals/mwre/78/1/1520-0493_1950_078_0001_vofeit_2_0_co_2.xml (V)
- Dawid (1984), "Statistical Theory: The Prequential Approach", *JRSS-A* 147(2):278-292 (forecasts judged sequentially on the data available at each step). https://doi.org/10.2307/2981683 (V)
- Diebold, Gunther & Tay (1998), "Evaluating Density Forecasts with Applications to Financial Risk Management", *International Economic Review* 39(4):863-883 (PIT test). https://doi.org/10.2307/2527342 (V)
- Gneiting, Balabdaoui & Raftery (2007), "Probabilistic forecasts, calibration and sharpness", *JRSS-B* 69(2):243-268. https://doi.org/10.1111/j.1467-9868.2007.00587.x (V)
- Gneiting & Raftery (2007), "Strictly Proper Scoring Rules, Prediction, and Estimation", *JASA* 102(477):359-378. https://doi.org/10.1198/016214506000001437 (V)
- Gneiting, Raftery, Westveld & Goldman (2005), "Calibrated Probabilistic Forecasting Using Ensemble Model Output Statistics and Minimum CRPS Estimation", *Monthly Weather Review* 133(5):1098-1118 (rolling training window). https://doi.org/10.1175/MWR2904.1 (V)
- Raftery, Gneiting, Balabdaoui & Polakowski (2005), "Using Bayesian Model Averaging to Calibrate Forecast Ensembles", *Monthly Weather Review* 133(5):1155-1174. https://doi.org/10.1175/MWR2906.1 (V)
- Gibbs & Candès (2021), "Adaptive Conformal Inference Under Distribution Shift", NeurIPS; arXiv:2106.00170 (coverage that adapts when the error distribution drifts). https://arxiv.org/abs/2106.00170 (V)

**Our errors.** Temperature error range: (a) conditioned on the wrong event (section 8), (b) not binned by scan time of day, so morning uncertainty was understated, (c) not seasonal (Nick 03:36Z: "error range has to be over a season, probably"). R-019 asks for residual CDFs by station × time-of-day bin × season, from data before each decision day, with PIT mean per bin; R-020 asks for P&L, Brier vs market and PIT split by local hour with mornings separate. MFW analogue: any fair-value or P(Up) model must be checked for calibration by seconds-into-window and by volatility regime, since that is how it is used.

**Rule.** Every predictive model reports, out of sample: reliability diagram or PIT histogram, Brier/log score *versus the market's own price* (the market is the benchmark forecast), all split by the variables the strategy conditions on (time to settlement, time of day, season, regime).

---

## 10. The market price is a forecast, and fills are not random

**Principle.** A binary contract price is approximately a probability, with known biases: a favourite-longshot bias, which Snowberg & Wolfers (2010) attribute to misperception of probabilities rather than risk-love, and prices that need not equal mean beliefs. Fills are selected: a resting order is filled more often when the counterparty knows more (adverse selection), so P&L conditioned on being filled differs from P&L of the price you quoted. Trade direction inferred from public feeds can be badly wrong on Polymarket.

- Wolfers & Zitzewitz (2004), "Prediction Markets", *J. Economic Perspectives* 18(2):107-126. https://doi.org/10.1257/0895330041371321 (V)
- Manski (2006), "Interpreting the predictions of prediction markets", *Economics Letters* 91(3):425-429 (price need not equal mean belief). https://doi.org/10.1016/j.econlet.2006.01.004 (V)
- Wolfers & Zitzewitz (2006), "Interpreting Prediction Market Prices as Probabilities", NBER WP 12200. https://www.nber.org/papers/w12200 (V)
- Snowberg & Wolfers (2010), "Explaining the Favorite-Long Shot Bias: Is it Risk-Love or Misperceptions?", *J. Political Economy* 118(4):723-746 (full text checked: using US horse-race win and exotic bets, "we find evidence in favor of the view that misperceptions of probability drive the favorite–long shot bias"; the evidence is from horse racing, not prediction markets). https://doi.org/10.1086/655844 (V)
- Page & Clemen (2013), "Do Prediction Markets Produce Well-Calibrated Probability Forecasts?", *Economic Journal* 123(568):491-513 (calibration worsens with time to expiry). https://doi.org/10.1111/j.1468-0297.2012.02561.x (V)
- Glosten & Milgrom (1985), "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders", *J. Financial Economics* 14(1):71-100 (adverse selection). https://doi.org/10.1016/0304-405X(85)90044-3 (V)
- Kyle (1985), "Continuous Auctions and Insider Trading", *Econometrica* 53(6):1315-1335. https://doi.org/10.2307/1913210 (V)
- Dubach (2026), "The Anatomy of a Decentralized Prediction Market: Microstructure Evidence from the Polymarket Order Book", arXiv:2604.24366 (q-fin.TR): public-feed trade direction matches on-chain truth on only ~59% of buckets; recommends on-chain OrderFilled events. https://arxiv.org/abs/2604.24366 (V: figures from the abstract: ~59% of buckets, panel mean 0.615, 95% CI 0.58-0.65)
- Qin & Yang (2026), Polymarket-v1 truth-aligned database, arXiv:2606.04217: tick-rule and bulk-volume classifiers near random; toxic flow linked to worse Brier. https://arxiv.org/abs/2606.04217 (V: abstract gives tick rule 49.83%, BVC 50.51%; true VPIN positively predicts Brier, i.e. worse forecasts)

**Implications.** (a) The edge to estimate is *model probability minus the price actually paid at the moment of decision*, from that token's own asks (SETTLED A1), not model minus last trade. (b) A maker simulation must model which orders get filled, or its P&L is biased up by adverse selection; the null in null_fair.py keeps timing and fills fixed and redraws only outcomes, which is valid for taker rules but does not test fill selection for maker rules. (c) Markets priced ≥0.99 / ≤0.01 are decided; decisions there are late triggers, not findings (MEMORY, Nick 18 Nov). (d) Any signal built from feed-inferred trade direction should be re-checked against on-chain fills.

---

## 11. Non-stationarity: edges drift, decay and switch regime

**Principle.** Return-generating processes change: regimes switch, published or crowded edges decay, and estimation windows face a bias-variance trade-off under breaks. An edge estimate is conditional on the period it came from; the forward test is a test of whether it still holds, and the record must be split by time block to show it.

- Hamilton (1989), "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle", *Econometrica* 57(2):357-384. https://doi.org/10.2307/1912559 (V)
- Pesaran & Timmermann (2007), "Selection of estimation window in the presence of breaks", *J. Econometrics* 137(1):134-161. https://doi.org/10.1016/j.jeconom.2006.03.010 (V)
- Lo (2004), "The Adaptive Markets Hypothesis", *J. Portfolio Management* 30(5):15-29. https://doi.org/10.3905/jpm.2004.442611 (V)
- McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", *Journal of Finance* 71(1):5-32. https://doi.org/10.1111/jofi.12365 (V)
- Page (1954), "Continuous Inspection Schemes", *Biometrika* 41(1/2):100-115 (CUSUM). https://doi.org/10.2307/2333009 (V)
- Adams & MacKay (2007), "Bayesian Online Changepoint Detection", arXiv:0710.3742. https://arxiv.org/abs/0710.3742 (V)

**Our errors.** Concentration hidden behind one number: nowcast's top-5 windows were 115-132% of total P&L (TESTING-EVIDENCE row 9). Temperature error ranges pooled across seasons. MFW October fills were used as a fixed benchmark for November behaviour.

**Rule.** Show P&L per window, per half, per 6-hour block (or per day/season), top-5 share and drawdown. Monitor live arms with a changepoint statistic rather than a fixed-sample re-test. A concentrated result is flagged and kept running, not discarded.

---

## 12. Cut the noise per decision before adding decisions

**Principle.** The windows needed scale with variance (section 2), so halving the SD per decision cuts the sample needed by four. The settlement outcome of a binary contract is the noisiest possible score: it is 0 or 1. If the market price is a martingale with respect to the public filtration (E[settlement | F_{t+h}] = p_{t+h}), then the P&L of a fill marked to the token's price at a later time t+h (the markout) has the same expectation as its settlement P&L, and by the law of total variance it has lower variance: Var(settlement P&L) = Var(markout) + E[Var(settlement P&L | F_{t+h})]. This is Rao-Blackwellisation applied to trade scoring. In betting markets the same idea is "closing-line value": beating the final pre-event price. Separately, any variable that predicts outcome but is not affected by the decision can serve as a control variate.

- Huang & Stoll (1996), "Dealer versus auction markets: A paired comparison of execution costs on NASDAQ and the NYSE", *J. Financial Economics* 41(3):313-357 (realised spread: execution price scored against the later price). https://doi.org/10.1016/0304-405X(95)00867-E (V). Full text checked, §7.1 pp. 320-321: "We estimate the post-trade revenues earned by the dealer on the basis of actual post-trade prices... defined as the realized half-spread" for a horizon τ; the effective spread minus the realised spread estimates "the amount lost to informed traders".
- Perold (1988), "The implementation shortfall: paper versus reality", *J. Portfolio Management* 14(3):4-9. https://doi.org/10.3905/jpm.1988.409150 (V). Full text checked: the shortfall is the gap between a paper portfolio and the real one and "measures not only... execution costs, but also the opportunity costs of not transacting".
- Deng, Xu, Kohavi & Walker (2013), "Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data" (CUPED, control variates), WSDM '13, pp. 123-132. https://doi.org/10.1145/2433396.2433413 (V)

**Limits.** The martingale assumption fails where prices are biased (favourite-longshot bias, section 10) or drift predictably before settlement, so markout is biased exactly where our edges may live. Use it as the screening and ranking statistic, and keep settlement P&L as the final check on the same cells. Mark to the price you could actually exit at (the token's own best bid) when the question is realisable P&L; mark to the mid when the question is forecast skill. Choose the horizon h in advance; report several.

**Application.** MFW: score each fill at t+10 s, t+30 s, t+60 s and at window end against the token's own book, alongside settlement; use the Binance (or Chainlink) move over the window as a control variate for the outcome. Temperature: score each decision against that bucket's price at later grid times and at the next METAR report. The variance reduction is unmeasured until run on MFW's October fills; that is the first measurement to make.

**Our error.** Every MFW and Temperature verdict so far scored fills only by settlement, so each test carried the full 0/1 noise.

---

## 13. Sequential testing: pre-set stop rules for success and for futility

**Principle.** Forward tests are watched continuously, and a fixed-sample p-value checked repeatedly inflates false positives. Sequential methods are built for continuous monitoring: Wald's sequential probability ratio test stops at the first crossing of a success or futility boundary; confidence sequences and e-values give intervals valid at every sample size at once, so results can be looked at any time without bias. A futility boundary gives "dead" a formal meaning: stop a cell when its always-valid upper bound on edge falls below cost (or below the target edge). That is evidence of no edge, which is what Nick's rule requires, and it is different from failing to reach significance.

- Wald (1945), "Sequential Tests of Statistical Hypotheses", *Annals of Mathematical Statistics* 16(2):117-186 (p. 118: at each stage the test either accepts, rejects, or continues; p. 125: the process "is terminated at the smallest value n" at which the sample enters the accept-H₀ or accept-H₁ region; p. 119: average saving of about 50% in observations versus the fixed-sample test, and no advantage when the sample size is fixed in advance). https://doi.org/10.1214/aoms/1177731118 (V)
- Johari, Koomen, Pekelis & Walsh (2022), "Always Valid Inference: Continuous Monitoring of A/B Tests", *Operations Research* 70(3):1806-1821. https://doi.org/10.1287/opre.2021.2135 (V). Preprint: Johari, Pekelis & Walsh, "Always Valid Inference: Bringing Sequential Analysis to A/B Testing", arXiv:1512.04922. https://arxiv.org/abs/1512.04922 (V)
- Howard, Ramdas, McAuliffe & Sekhon (2021), "Time-uniform, nonparametric, nonasymptotic confidence sequences", *Annals of Statistics* 49(2):1055-1080; arXiv:1810.08240. https://arxiv.org/abs/1810.08240 (V)
- Ramdas, Grünwald, Vovk & Shafer (2023), "Game-Theoretic Statistics and Safe Anytime-Valid Inference", *Statistical Science* 38(4):576-601. https://doi.org/10.1214/23-STS894 (V); arXiv:2210.01948. https://arxiv.org/abs/2210.01948 (V)

**Application.** Every forward cell is registered with: score (markout at h, plus settlement), success boundary (lower bound above cost), futility boundary (upper bound below cost), and a maximum sample after which it is reported as "inconclusive, ranked", not dead. Sections 7 (which cell to observe next) and 13 (when to stop observing one) work together.

**Our errors.** Fixed 100-window tests checked once and read as final; no futility rule, so "dead" was assigned by missing a success bar.

---

## 14. Capacity and sizing: an edge is worth edge × fillable size

**Principle.** A rule's value is its edge per unit times the size that can be filled at that edge, net of the price impact of filling it. Depth at the decision price, queue position for resting orders, and impact (Kyle's λ) set capacity. Sizing under an uncertain edge should be fractional Kelly at most: full Kelly on an overestimated edge is ruinous, and parameter uncertainty argues for shrinking the bet in proportion to it.

- Kelly (1956), "A New Interpretation of Information Rate", *Bell System Technical Journal* 35(4):917-926. https://doi.org/10.1002/j.1538-7305.1956.tb03809.x (V)
- Baker & McHale (2013), "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion", *Decision Analysis* 10(3):189-199. https://doi.org/10.1287/deca.2013.0271 (V)
- Almgren & Chriss (2001), "Optimal execution of portfolio transactions", *Journal of Risk* 3(2):5-39. https://doi.org/10.21314/JOR.2001.041 (V)
- Kyle (1985), section 10.

**Application.** Every cell's ranking row carries: median and 10th-percentile depth at or better than the decision price on that token's own asks at decision time, fills per day, $ edge per day at that depth, and the share of the target ($500/day MFW, $200/day PK) it can reach. A cell that is profitable but too small is labelled "capacity-limited", kept, and considered for stacking with others (section 4). Its edge is not in doubt; its size is.

**Our errors.** PK gas daily failed the $200/day bar on size (best $11.74/day) and PK perps failed on size, after the edge work was done; nothing in the test design measured capacity first. MFW per-market caps ($150) and wallet size ($300/$450) were not built into cell rankings.

---

## 15. Screening a new decision-market type

Apply in order; each step names the section it rests on.

1. **Settlement and information set (8).** Write down the exact resolution source, its timestamps, and the publication lag of every input. Define the decision grid (fixed times or event-driven by an observable event). Nothing in the decision or training data may be placed relative to an outcome-defined time.
2. **Market mechanics (10).** Per-token books, tick size changes, min size, fees and rebates, taker delays, and what the public feed does and does not tell you, from primary docs and a live probe. Mark prices ≥0.99/≤0.01 as decided.
3. **Benchmark forecast (9, 10).** The market price at decision time is the forecast to beat. Score your model against it with Brier/log, out of sample, split by time to settlement and time of day/season.
4. **Noise and power (2, 12).** Choose the lowest-variance unbiased score available (markout at a pre-set horizon plus settlement). Measure σ of P&L per decision under that score. Compute the decisions needed to detect the target edge. Plant a known edge and a null through the full harness; it must detect the first and not the second at that sample size. If the market cannot give that sample in reasonable time, say so: the test is a ranking aid only.
5. **Capacity first (14).** Measure depth at the decision price and the $/day ceiling before deep edge work; a market that cannot reach the target at any plausible edge is ranked as capacity-limited.
6. **Generate candidates broadly (4, 7).** Many distinct mechanisms (taker/maker, phase of window, signal source), counted and logged so overfitting can be deflated (6).
7. **Estimate, shrink, rank (5, 6).** For every cell: raw edge, shrunk edge, interval, probability edge > costs, deflated Sharpe or FDR q-value, shape of P&L. Rank. Delete nothing; unrun cells are "untested".
8. **Forward paper the band (7, 11, 13).** Run the top band in parallel on live data with pre-registered sequential boundaries; allocate new cells and promotions by Thompson sampling / top-m identification; monitor for drift. A cell leaves only when its own always-valid upper bound falls below cost.
9. **Real capital (1, 14).** Promotion, sized at fractional Kelly on the shrunk edge and capped by measured capacity, to real money is a separate decision with its own, higher threshold and Nick's approval. Never trade or stage orders from this process.

---

## 16. Error-to-principle map

| Error (evidence) | Principle violated | Section |
|---|---|---|
| p95 gate used as kill: nowcast +$1,387/p95.2, +$1,060/p94.2; M1 +$135/p92.9; fast2 "0/144" with 84/331 profitable (mfw-clone 3323c77b, 42fa7462, f282978f; reviewer a80a7052) | Test used as a decision rule; asymmetric losses ignored | 1, 5, 6 |
| Known profitable trader passed 2/44 blocks; σ $24-106 vs edge $2-5 (AUDIT B.1, B.2) | No power; no positive control before verdicts | 2 |
| Both arms required to pass (PREREG-2026-11-19-nowcast-taker-s120.md) | Intersection-union test on correlated arms | 3 |
| ~900 of 1,020 sequences never scored, counted as failed (b96ddafd) | Unpulled arm treated as a loss | 7 |
| Decision time from the day's extreme (us_l15_loader_nolgb.py:117, 95f164e5e; R-006) | Non-predictable strategy (stopping-time leak) | 8 |
| Error range trained 15 min before past extremes, applied at every scan time (grid_layer.py:168-173, 6d27ad3c6; R-017) | Training-set leak; conditional miscalibration | 8, 9 |
| Error range not by time of day or season; morning losses (R-019, R-020) | Calibration not conditioned as used | 9 |
| Top-5 windows 115-132% of nowcast P&L, hidden by one percentile (ranked_table.md) | Non-stationarity / concentration not shown | 11 |
| One arm at a time; prereg parked for "new windows" (MEMORY 20 Nov) | Sequential allocation without explore-exploit | 7 |
| Every verdict scored by settlement only (all MFW and Temperature runs to date) | Avoidable 0/1 noise; no markout or control variate | 12 |
| Fixed 100-window tests read once as final; "dead" assigned by missing a success bar | No sequential design; no futility boundary | 13 |
| PK gas $11.74/day and PK perps failed on size after edge work (MEMORY 20 Nov) | Capacity not measured first | 14 |

---

## 17. Citation check list

Checked 21 Nov 2026 04:55-05:10Z. Every citation is now V. V = confirmed against a primary listing: 48 DOIs resolved in one Crossref query, plus 4 journal versions found by Crossref bibliographic search (title, authors, journal, year, volume, pages all matched the text; two page ranges corrected: Almgren & Chriss 5-39, Deng et al. 123-132); 12 arXiv IDs against their arXiv abstract pages; NBER w12200 and w25456 against nber.org; SSRN 2460551 and 2308659 and the ICML 2012 paper via search listings. No citation is used for a number in our results; they support principles only.

**Maths check (21 Nov, 05:20-05:35Z), script `reviewer/mathcheck.py` in project files.**
- Section 2: the power formula and every figure in "Our numbers" were recomputed and reproduce AUDIT B.2 (k = z₀.₉₅ + z₀.₈ = 2.486; nowcast ≈ 2,370 windows; $22 net at 100 windows; M1 ≈ 200 windows). Correction made: μ is the gap from the null's mean (net edge plus fees), now stated.
- Section 3: P(A and B) ≤ min(P(A), P(B)) holds for any events. For bivariate-normal test statistics with correlation ρ ≥ 0, the joint power rises with ρ (Slepian's inequality) from the product at ρ = 0 towards the weaker arm. Simulation, arm powers 0.60 and 0.50: ρ = 0 gives 0.300, ρ = 0.6 gives 0.399, ρ = 0.9 gives 0.468, ρ = 0.99 gives 0.499. The AND rule's false-positive rate is below α (0.25% at ρ = 0, 3.2% at ρ = 0.9 against 5% per arm): it buys a stricter false-positive rate than was asked for, paid for in power. Statement correct as written.
- Section 4: $2 × 288 = $576; $100 × √288 = $1,697; daily Sharpe 0.339; × √365 = 6.48; P(Z < −0.339) = 0.367; (2/0.339)² = 34.7 days. Correct, assuming independent windows and a normal approximation for daily sums.
- Section 12: if p is a martingale, E[Y − c | F_{t+h}] = p_{t+h} − c, so the means are equal and Var(Y − c) = Var(p_{t+h} − c) + E[p_{t+h}(1 − p_{t+h})], exactly (law of total variance); it also holds for sums of fills, since the second term stays non-negative. Simulation (binary on Brownian motion, 300 s window, buy at 60 s with a planted 2-cent edge, mark at 90 s, 300,000 trades): mean settlement P&L 0.0204 ± 0.0009, mean markout 0.0206 ± 0.0002; Var 0.2181 = 0.0164 + 0.2016. In that toy the markout needs 13× fewer trades. The real reduction for MFW depends on how much the price moves after a fill and is unmeasured.

**Claim check (21 Nov, 05:10-05:40Z).** Each claim the file attributes to a paper was checked against the paper's own text or abstract (68 citation bullets):
- Supported by full text (supporting sentence quoted from an open copy): Neyman & Pearson; ASA statement Principle 3 (verbatim); Button et al.; Bailey et al. 2014; Bailey & López de Prado DSR; Thompson; Auer et al.; Diebold, Gunther & Tay; Gneiting et al. 2005 (sliding 40-day training window, skill declining beyond 45 days from seasonal bias, §3a); Page & Clemen (well calibrated near expiry, biased far from it); Glosten & Milgrom; Kyle; Pesaran & Timmermann (working-paper version); Harrison & Pliska, Wald, Brier, Grinold, Huang & Stoll, Perold, Dawid, Page, Berger, Clarke et al., Efron & Morris, Efron 2011 and Snowberg & Wolfers (PDFs supplied by Nick, 21 Nov 05:54-06:22Z; Berger 1982 Theorem 1: the intersection-union test is level α, but "might be quite conservative in that the maximum consumer's risk (size) might be much less than α"; Clarke et al. eq. 6, the generalised law IR ≈ TC × IC × √N, with TC "a simple scaling factor"; Efron 2011 abstract and §1: "the largest few of the z_i's are likely to substantially overestimate their corresponding μ_i's" ("the winner's curse"), corrected by Tweedie's formula; Efron & Morris 1975: Stein-type shrinkage rules give "less than half" the mean squared error of the sample means in their examples; Dawid's summary: the prequential approach "is founded on the premiss that the purpose of statistical inference is to make sequential probability forecasts for future observations"; Page plots the cumulative score S_n and acts "whenever S_n − min S_i > h", with the average run length measuring false alarms when quality is good and detection delay when it is poor; Brier defines the verification score P, the mean squared difference between forecast probabilities and outcomes, and shows it is minimised by forecasting the observed relative frequencies, p. 1).
- Supported by abstract: all other cited papers except those below.
- Corrected after checking: Snowberg & Wolfers (misperception, not risk-love); PBO (ranks below the median configuration out of sample); Harvey & Liu in section 6 (lack of power, not "many" missed discoveries); Bergmeir & Benítez (scope narrowed).
- Every citation's claim has now been checked against the paper itself (full text) or its abstract. None remains unchecked.

| Citation | Status |
|---|---|
| All 52 DOIs (Crossref), 12 arXiv IDs (arXiv abstract pages), NBER w12200 and w25456 (nber.org) | V |
| Bailey & López de Prado SSRN 2460551; Bailey et al. SSRN 2308659; Kalyanakrishnan et al. ICML 2012 pp. 655-662 | V (search listings; SSRN pages block automated access) |
| Corrections made during checking | Almgren & Chriss pages 5-39; Deng et al. pages 123-132; Johari arXiv preprint has three authors (Koomen only on the journal version); PBO cited by its Crossref record (online Sept 2016), as Crossref lists no print volume |

**Corrections in v2 (Nick's review, 04:04Z).** Section 3: the power of an AND gate equals the product of arm powers only for independent arms; for correlated arms it lies between the product and the weakest arm. Section 4: breadth gets a square-root caveat with a worked example. Section 5: the 34-window ranking is stated to be mostly noise. New sections 12 (variance reduction), 13 (sequential testing), 14 (capacity and sizing); screen and error map updated.

**v3 (05:05Z):** citations checked; see section 17.

**v6 (05:35Z):** maths in sections 2, 3, 4 and 12 checked; see section 17.

**Confidence 9/10** that every claim and citation is correct and that sections 1-14 are mutually exclusive and jointly cover the errors listed. Raised to 9/10 on 21 Nov 06:10Z: every claim is now checked against full text (22 papers) or the abstract (the rest), and the maths is checked. What remains below 10: claims supported by abstracts rather than full text, and the simulated 13x markout gain, which is a toy-model figure until measured on MFW's fills. Overlap that remains by design: sections 5 and 6 both treat selection bias (5 as estimation, 6 as testing); sections 8 and 9 both treat the Temperature error range (8 the leak, 9 the conditioning); sections 7 and 13 both govern forward tests (7 which cell to observe, 13 when to stop). The size of the markout variance reduction (section 12) is a claim about direction only until measured on MFW's fills.
