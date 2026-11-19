# Lag check (exploratory, fixed before running; 19 Nov ~02:35Z)
Why: the hourly test (803825d7) cannot see a lag of seconds to minutes (SETTLED B1). Only minute perp data reachable: Hyperliquid xyz:SP500 1 m candles saved in pkarbs (12 Nov 21:38Z - 16 Nov 08:58Z). That covers the whole 13 Nov SPY event (overnight + session) and the 16 Nov event up to Monday 08:58Z. Every minute-data host tried from this container is blocked (list in LAG-RESULT.md). n is one-and-a-bit events: descriptive only, no verdict.
- Fair p_up(t) = Phi((ln(P_t/C0) + mu)/sigma(tau)); P_t = close of the 1 m candle ending at or before t (known before t); C0 = prior ^GSPC close; sigma(tau), mu interpolated in hours-to-close tau from the TRAIN sigma_k, mu_k (result.json); tau > 23 h: sigma_23 x sqrt(tau/23).
- Polymarket implied p_up per print: price if the print is on Up, 1 - price if on Down (own-token prints only, no books).
- Perp move: a minute where |ln(P_t/P_t-5m)| >= 10 bp; after one, skip 10 min. Model jump dp = p(t) - p(t-5m).
- PM pre-level: median implied p_up of prints in [t-15m, t-5m]; none = move not measurable, counted.
- Lag: seconds from t to the first print whose implied p_up has covered half of dp from the pre-level (direction-aware). Censored at 30 min.
- Stale $: taker BUY prints with price < fair(token) - fee(price) - 0.01, summed in USD, whole event and inside lag windows; realised P&L per share at resolution for those prints.
