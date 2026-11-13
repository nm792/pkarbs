# LOCKED RULE: wholesale (RBOB proxy) signal for Kalshi gas near-strike strikes (written 11 Nov before testing)
Data: FRED DGASNYH (NY Harbor conventional gasoline regular spot, daily, public CSV; ends 3 Nov 2026 at fetch time). Rack and station data are not available.
Signal: sign of the 3-trading-day change in DGASNYH ending at the last value known before the market opens (change from t-3 to t-0 where t-0 = the close two calendar days before the event date, i.e. the latest print available at 13:00Z on D-1).
If RBOB rose, expect retail AAA to rise: buy YES ('above'); if it fell, buy NO. Skip if the change is under 1 cent/gal in absolute value.
Strikes: within 3c of the prior-day AAA value, YES mid 25-75c one hour after open. Fill at ask (YES) or 1-bid (NO), Kalshi fee 0.07 p(1-p), hold to settlement.
Series: national daily plus the 12 state series already cached (CA, TX, FL, NY, IL, NJ, WA, NC, OH, PA, GA, VA), all with the same NY Harbor series (no per-region variants).
One test, no variants. Held-out: first half of the dates = train, second half = TEST (headline), event-clustered 95% CI, sign-flip placebo 2000 draws.
PASS only if TEST gap > 0 with lower bound > 0, placebo z >= 2.0, hit rate above market-implied, and >= 100 TEST strikes from >= 40 events (the data window may be too short: then the verdict is UNPROVEN with the count).
