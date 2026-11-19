# DESIGN v1: pre-release nowcast of the AAA national gas average, backtest and forward test (19 Nov 2026, ~05:30Z)

Goal: find and build un-publicised, automated edges that reliably reach $500/day. This note fixes the nowcast and the test BEFORE any scored run on new data. SETTLED.md read at e2a25c41beffd3f4438590a691fc2ed07402838b.

## 0. What has already been seen (disclosure)
On 19 Nov ~04:50Z I ran an exploratory first version on the 28 resolved Polymarket events 22 Oct to 18 Nov: model `scan/gas_window/nowcast.py` (blob 4001a87f), scorer `score.py` (blob 8d70ea6), parameters fixed before looking (5 AR lags, ridge alpha 10, expanding window; nothing tuned on those days). Result: top-bracket hit 54% vs market favourite 61% at 16:00Z D-1, 61% vs 82% at 03:00Z D, 61% vs 89% at 05:00Z D (28 events; without 14 Nov 52/59, 59/81, 59/89). Those 28 days are now a DEVELOPMENT sample: they were seen, so they are NOT evidence for or against v1. The test sample for v1 is forward only (section 6).

## 1. Target and venues
Target: the AAA national regular price shown at 10:00 ET on day D (4 decimals via Kalshi expiration_value; Polymarket uses the same AAA table, rule text in the event description). Brackets: Polymarket 6 buckets per event (`less than X`, 1c-wide `between X and X.0099`, `X+`), tokens Yes and No per bucket. Kalshi KXAAAGASD (strikes 0.5c apart, YES = price strictly greater than strike) is a second venue. IMPORTANT: Kalshi trading closes 23:59 ET on D-1 (close_time 04:59Z, 03:00 ET D is after close), so a 03:00 ET entry exists only on Polymarket; Kalshi can be scored only at the earlier times. Kalshi is not cleared for us (A6, A7): analysis only, its size reported separately.

## 2. Decision times (fixed)
Primary: 03:00 ET on D (before the observed sweep, 03:14 to 03:36 ET, see sweep.py). Earlier, for comparison: 22:00 ET D-1 and 11:00 ET D-1 (16:00Z D-1 in winter). Kalshi: 11:00 ET and 22:00 ET D-1 only.

## 3. Inputs, and what is known at each decision time (no lookahead)
- AAA national prints through D-1 (10:00 ET on D-1 is before all three times). Source in backtest: Kalshi expiration_value, contiguous daily since 26 Mar 2026 (238 days).
- NY Harbor and Gulf Coast conventional gasoline spot (FRED DGASNYH, DGASUSGULF, $/gal, daily): at 11:00 ET D-1 only values dated D-2 or earlier, at 22:00 ET and 03:00 ET values dated D-1 or earlier. LIVE CAVEAT: FRED publishes with a lag; live use needs EIA or a market data source with the same date convention. Not solved.
- NOT used in v1 (not fixed ex ante, to be added only as a pre-registered v2): state-level AAA prints (jgreathouse9/AAAGas MasterGas.csv since Nov 2024, no LICENSE file found: internal research use only; staleness unchecked), FuelRipple (not read), GasBuddy, intraday RBOB futures, anything published at the overnight release itself (unknown publisher, see section 9).

## 4. The nowcast (fixed formula)
Target variable: delta = P_D minus P_{D-1} in cents. Features (11): the last 5 daily changes of the national print; spot change NYH 1, 3, 5 days; Gulf 1 and 5 days (last known spot, lags as in section 3); retail minus NYH spot (cents). Model: ridge, alpha 10, standardised features, expanding window refit every day on all days strictly before D, minimum 60 training days, training start 26 Mar 2026. Predictive distribution: Normal(P_{D-1} + mu, sigma), sigma = max(training residual SD, 0.5c). Bracket probability = probability mass inside the bracket bounds (1c brackets: bound minus 0.0005 / plus 0.0005 convention fixed in nowcast.bucket_bounds). No parameter may change after this commit; a change is a new version number and a new forward sample.

## 5. Entry rule, fees, fills
Primary rule: at the decision time buy YES of the bracket with the highest nowcast probability p, at that token's OWN best ask a, only if p - a >= 0.05 + fee(a). One bracket per event. Secondary (reported, not the verdict): any Yes or No token of the event with p - a >= 0.05 + fee. Never price No from Yes (A1, separate books).
Fees: Polymarket gas events fee schedule NOT yet read from docs: assumed 0 with sensitivity 2% of price; label ASSUMED. Kalshi taker 0.07 p (1 - p) (A9 inputs), Kalshi maker 0 assumed.
Fill assumptions: (a) Development and any back period: no historical books exist, so fills are credited only against taker BUY prints that actually occurred on that token inside [t, t+10 min] at a price <= a_limit = (first observed taker price in the window) + 0.01, quantity = 10% of printed size (we are taker, no queue); (b) Forward period: pm_gas_books.py (blob f14392db) records each token's own asks and depth every second from 02:50 to 03:45 ET; fills are credited against the real book at t, size capped at depth within 2c of the best ask and $100 per event, no more. Each reported edge states which of (a) or (b) it uses.

## 6. Samples and looks
Development sample (seen, plumbing only): 22 Oct to 18 Nov 2026 (28 Polymarket events). Test sample: Polymarket events with D >= 20 Nov 2026, scored once when 30 events have resolved (about 19 Dec), nowcast frozen at this commit. No interim peeks at hit rate; plumbing checks only. Additional OOS history for the hit-rate comparison on Kalshi only (information): 1 Apr to 21 Oct 2026, at 11:00 ET and 22:00 ET D-1, compared with the Kalshi favourite from candle bid/ask; this stage may be run now because the model was never fitted to it, but the walk-forward uses the same frozen formula.

## 7. Pass and fail bars
Hit-rate test (primary, 03:00 ET, Polymarket forward sample, n >= 30 events): PASS only if nowcast top-bracket hit rate exceeds the market favourite's at the same timestamp by at least 5 percentage points AND the paired day-bootstrap 95% CI of the difference has a lower bound above 0. Also report log-loss difference. Otherwise FAIL: "nowcast does not beat the favourite". The favourite at 03:00 ET is the highest YES last price or mid; if it is already >= 0.95 on most days the nowcast has nothing left to find, which is itself a FAIL for this route.
Economic bar: A9, $200/day CI lower bound before rebates, 10% slice. Polymarket whole-event volume is $0.9k to $18k (median about $3.4k), so even perfect knowledge at 03:00 ET is capped at about $26/day at stale prices in the sweep window (sweep.py, 28 days). A hit-rate PASS therefore does NOT make Polymarket gas tradeable at the bar; it would show where the information sits. Kalshi sizes are reported separately.

## 8. Planted-edge and placebo checks (before any real forward run)
(i) Unit tests: `test_nowcast.py` (planted autoregression recovered, null gives no skill, no lookahead, bracket parsing), `test_sweep.py`, `test_pm_gas_books.py`, `test_aaa_watch.py`. (ii) Oracle plant on the development sample: replace mu by the true delta plus noise of known SD; the scorer must show top-bracket hit rising as noise falls and the pass rule must fire only below a stated noise level; a random-delta placebo must FAIL. This oracle test is still to be written and committed before the forward run; if it cannot fail it is not a test.

## 9. 14 Nov and the open source question
14 Nov is reported with and without it everywhere; a verdict stands only if both versions agree. AAA release: what drops, when and in which time zone, is UNCONFIRMED. Observed: a sweep of winner tokens across all buckets at 03:14 to 03:36 ET (08:14 to 08:24Z in November, 07:15 to 07:36Z in October) on 24 of 28 days. gasprices.aaa.com is reachable from this session after the network card but returns HTTP 403 (Cloudflare) to a plain request; I do not work around that block. Fetch of the page for timestamping has to run on the server agent via it/ (aaa_watch.py, blob a2cd54b1) and may meet the same block.

## 10. Confidence
7/10 that the design is complete and leak-free; 5/10 that live inputs (spot lag, release time) can be sourced at 03:00 ET. To reach 9: confirm the Polymarket fee schedule from docs.polymarket.com, a live spot source with date convention, and the first week of real 03:00 ET books.
