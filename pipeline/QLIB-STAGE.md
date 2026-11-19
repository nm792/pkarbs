# Stage 2: qlib / LightGBM / Alphalens-style analysis (19 Nov 2026)

Nick's instruction (04:09Z): apply the techniques from the repos he sent, withdraw the "can't carry $500/day" verdict, report what each technique found with limits. **Status of "can this reach $500/day": unknown.** Nothing below is a verdict.

Tools: qlib installed from source (microsoft/qlib main, imports `qlib.contrib.eva.alpha.calc_ic` and `calc_long_short_return`), LightGBM 4.7.0, alphalens-reloaded. RD-Agent (LLM factor mining) was NOT run: it needs an LLM API key and its docker runtime; I did automated factor mining over an Alpha158-style grid instead (below).

Code: `panel.py` (features), `ext.py` (Yahoo drivers), `model.py`, `model_ext.py`, `alphalens_run.py`; tests in `tests/` (20 pass, incl. no-lookahead of every feature and purge of unresolved labels). Outputs: `out/model1/`, `out/model_ext/`. Panel pulled from cached `/v2/trades` (gamma keyset events, `series_slug` history); commit in the report message.

## Panel (what the model saw)
17,445 rows = 6,665 markets x token x decision time (10 min, 1 h, 6 h, 24 h before gamma endDate), 148 series (non-sport, non-esport, non-crypto, non-weather), 158 features. Label = edge = win - causal fill (first BUY print of that token after the decision). Every feature uses that token's own prints strictly before the decision; the other token's features use the other token's own prints. 12,986 rows are finance daily Up/Down, 2,629 tweet counts, the rest ~1,800 across 100+ small families (<= 40 events each in the 30-day window): "all eligible series" is mostly finance daily.
Features follow qlib Alpha158 operators with calendar windows (5 m, 15 m, 1 h, 3 h, 6 h, 24 h): ROC, MA(vwap), STD, BETA, RSQR, RESI, MAX, MIN, QTLU, QTLD, RANK, RSV, IMAX, IMIN, KMID/KLEN/KUP/KLOW, CNTP, SUMP, plus volume, taker imbalance, average size, and PM-specific: other token's last price and 1 h change, sum of the two own last prices (staleness), bid-ask bounce, time since last print, market age, hour, weekday, horizon.

## 1. LightGBM combination, purged walk-forward (`out/model1/model_result.json`)
Expanding window, 5 test folds over the last 50% of time (from 25 Mar 2026), training rows must have ENDED before the fold starts. 250 trees, one config (not tuned; no config search).
- qlib `calc_ic` on OOS predictions, one token per market (6,526 rows, 197 days with >= 10 rows): **IC -0.016 (t -1.0, p 0.32)**, rank IC -0.051. All rows: IC -0.009. By horizon (days): 10 m +/-, 1 h IC +0.075 (28 d, p 0.38), 6 h -0.009 (158 d), 24 h -0.030 (72 d): none significant.
- Baseline, last price alone: IC +0.031 (t 1.86, p 0.064): the model does not beat the favourite-longshot baseline.
- qlib long-short (top vs bottom 20%): edge -0.006. Quantile table (global quintiles of the score): mean edge Q1 +0.006, Q2 -0.019, Q3 -0.020, Q4 -0.018, Q5 -0.002: not monotone.
- Sizing from the model (one side per market, net = predicted edge - 0.04 p(1-p) fee, 10% of the printed shares in the fill window): thr 0.02: $29/day deployed, P&L +$1.28/day (day-bootstrap CI -$0.99 to +$3.66), placebo (scores permuted within day) mean $0.49, 95th pct $3.99; top-5 days = 117% of P&L. Same story at thr 0.04 and 0.06. Not distinguishable from the placebo.
- Top importance: last price, other token's last price, RSQR_24h, other-token 1 h change, average size, bounce.

## 2. Alphalens (`out/model1/alphalens.json`)
`alphalens.utils.get_clean_factor` + `performance`: OOS score vs edge. Mean edge by score quintile: Q1 +0.002, Q2 +0.005, Q3 +0.013, Q4 -0.004, Q5 -0.014 (standard errors about 0.011). IC (Spearman, as Alphalens computes it) -0.051 over 197 days. No usable signal. Note: Spearman IC against a binary-payoff edge is biased (a calibrated market gives non-zero Spearman); we use qlib's Pearson IC as primary.

## 3. Factor mining (Alpha158-style grid) with multiple-testing control (`out/model1/mining_all.json`)
627 feature x horizon cells, OOS one-token Pearson IC per day (qlib `calc_ic`), BH q = 0.10: **23 discoveries** (rerun of the first pass, which listed 24: the merge and median-fill differ slightly). By horizon: **6 h: 16 discoveries on 158 days (3,545 rows)**, 1 h: 5 (32 days, 433 rows), 10 m: 1 (11 days), 24 h: 1 (75 days).
- 6 h (strongest evidence, IC 0.05 to 0.075): up-tick share and drift positive (CNTP_24h +0.069 t 3.9; CNTP_6h +0.063; SUMP_24h +0.059; KMID_24h +0.066), short-term range and bounce negative (STD_5m -0.065, KLEN_5m -0.063, KLOW_5m -0.072, MAX_5m -0.061, IMIN_24h -0.075, MA_24h -0.050). Coherent story: tokens drifting up on many small up-ticks and not currently jumpy keep winning more than their price implies. Features are strongly correlated, so 16 is not 16 independent findings.
- 1 h (IC 0.18 to 0.22, t 3.3 to 3.95 on 32 days): CNTP_6h, CNTP_24h, BETA_6h, SUMP_6h, sum of the two own last prices. Thin sample. 10 m: ROC_15m -0.144 (11 days).
- **Promising, unconfirmed.** Selection and evaluation use the same OOS data, so these IC values are optimistic.

## 3b. Horizon-specific models (`out/model_h/model_h_result.json`)
6 h rows only (6,836; 3,252 OOS one-token rows, 158 days): LightGBM IC +0.020 (t 0.87); ridge on 11 of the mined 6 h features (chosen from the table above, so in-sample for selection) IC +0.017 (t 0.89). Sizing thr 0.04: P&L +$0.46/day (CI -$1.6 to +$3.2) vs placebo p95 $1.7. 24 h (3,305 rows, 72 days): LightGBM IC -0.019, top score quintile mean edge +0.036 (ROI +10.5%) vs -0.02 to -0.05 for the other quintiles; sizing +$1.08/day (CI -$0.77 to +$3.10), placebo mean -$1.09, p95 $1.68. So the single-feature IC at 6 h (about 0.07) does not become a combined-model IC of the same size on this sample; the top quintile at 24 h is the only monotone-looking result and rests on about 200 rows.

## 4. External drivers: Yahoo 5 m underlying (`out/model_ext/model_ext_result.json`)
32 finance Up/Down series, 2,548 rows, 1,047 markets, 62 days (Yahoo 5 m reaches back 60 days). Features: underlying return since the prior close (signed to the token's direction), z-score by the series' own daily vol, 1 h and 5 m underlying returns. Walk-forward 4 folds from 50% of the 62 days, 599 OOS rows, 29 days with >= 6 rows.
- PM-only features: IC -0.113 (p 0.045, i.e. over-fit); PM + underlying: IC -0.107 (p 0.039); underlying only: IC +0.001. Raw (no model) OOS IC of underlying return since close: +0.083 (t 1.85, p 0.075); z-score +0.036; 1 h return +0.057.
- Underlying signed move vs outcome correlation is 0.42 at 6 h, 0.31 at 1 h, 0.26 at 10 m: the underlying predicts the winner, but the price already reflects most of it (correlation with edge about 0.03). Sizing: negative or zero everywhere; placebo p95 about $5/day.
- Limits: 29 OOS days; far too few to detect an IC of 0.05.

## Size (what these numbers can and cannot say)
The panel samples up to 220 events per series and the top 2 markets per event, so printed flow and therefore dollar P&L here are lower bounds for the series, not totals. Even so, 10% of the printed shares in the model's qualifying fill windows is $4 to $29/day deployed. Whether an edge of the size seen (IC 0.02 to 0.07) can scale to $500/day depends on full-population flow, which was not measured.

## Limits (all of the above)
- Data: 6,665 markets; the multi-series universe is dominated by finance daily; non-daily families have <= 40 events. Per-day cross-sections are 10-30 rows, so IC t-stats rest on 28-197 days.
- Fills are first BUY prints, not book snapshots; sizing assumes 10% of printed flow; fee fixed at 0.04 p(1-p) for every series (political series pay 0, so politics sizing is conservative).
- Features use prints only; no recorded books, Goalserve, PandaScore or perps were joined (they cover sports, esports and crypto, excluded by Nick).
- Hyperparameters were not tuned (one config); a tuned or horizon-specific model could do better or worse. Not tried: RD-Agent, ranking objectives (LambdaRank), per-series models, longer history by pulling more events, multi-day horizons.
- Multiple testing: section 1 one config, section 3 627 cells (BH), section 4 three feature sets x 3 sizing thresholds; not corrected across sections.
