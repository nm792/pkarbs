# LOCKED RULE: buy the early leader in Kalshi index markets (written 11 Nov before any price data was looked at)
Series (fixed): KXINXU (S&P 500 above/below, hourly), KXNASDAQ100U (Nasdaq above/below, hourly), KXDJIAH (Dow hourly), KXINXZ (S&P up, daily), KXNASDAQ100Z (Nasdaq up, daily).
Searched for Kalshi Dow and single-stock open/close series: found Dow only as KXDJIAH (hourly) and KXDJIA15M (15-minute, excluded as outside the question); no single-stock open/close series exists (only KPI/CEO markets).
Rule: for every resolved market in these series (live API + /historical, random sample of up to 300 markets per series across the whole available history), one hour after open take the FAVOURED side
(YES if mid >= 50c, else NO) at the ask (YES) or 1 - bid (NO), if its price is between 55c and 95c; skip if the market closes less than 30 minutes after that checkpoint. Kalshi fee 0.07 p(1-p). Hold to settlement.
Metric: favourite's average ask vs its win rate, gap = win rate - ask - fee, net per $, event-clustered 95% CI, size = 10% of $ traded in the 2 hours after the checkpoint (x0.5 taker-buy share), $/day.
Held-out: first half of dates = train, second half = TEST (headline). Placebo: outcomes redrawn as Bernoulli(ask) with the same fees, 2000 draws (z of real TEST vs placebo).
PASS (per series) only if TEST gap > 0 with CI lower bound > 0, placebo z >= 2.0 and >= 100 TEST markets from >= 40 events. Otherwise UNPROVEN/FAIL. One test, no variants of band, horizon or side.
