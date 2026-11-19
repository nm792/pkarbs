# SPY daily Up/Down vs Yahoo 5m: result (rule: RULE.md, locked at 6a50f97226 before scoring)

Run: `python3 -I pipeline/spy_lag/spy_lag.py /home/user/spy pipeline/spy_lag/out`, code in the commit that adds this file, output `out/result.json`.
Inputs: Yahoo SPY 5 m bars (`out/spy5m.json`, fetched 19 Nov ~04:05Z), Reviewer's `perp-spy-daily/data` Polymarket events and trades (reviewer branch). 59 events, 25,521 taker BUY prints, TEST = 8 Oct-18 Nov (30 days, 8,206 prints).

**Verdict (locked rule): FAIL.** TEST realised per share -0.032 (95% CI -0.139 to +0.084), $-15/day at 10% of qualifying flow (CI -$76 to +$36); 2,680 qualifying prints, $81k of printed notional over 30 days.
- Ex-ante edge by the model 0.116 per share vs realised -0.032: the model's edge is mostly its own error (sigma by hours-to-close is estimated on 40 train days and is not smooth: 29 bp at 1 h, 30 bp at 2 h, 16 bp at 3 h).
- Last 3 h to the close: -0.190 per share (CI -0.39 to +0.01), 420 prints, 13 days. More than 3 h out: +0.020 (CI -0.10 to +0.13).
- TRAIN (27 Aug-7 Oct): +0.151 (CI -0.026 to +0.323), $100/day (CI -$16 to +$250): not significant either, and the sign flipped on TEST.
- Controls: planted 5c edge found (TEST +0.051, CI +0.009 to +0.101); null (q = model p) 0 trades; sign-flip placebo +0.021 on TEST (expected below 0, so there is no signal beyond chance, same as the Reviewer's hourly test).
- Size: qualifying prints are $2.7k/day of printed notional; 10% of that is $270/day. Even a true 0.10 per share edge on all of it would be about $27/day. SPY daily cannot carry $500/day at current volume (Reviewer: Nov events average $8k per event).
- Limits: 5-minute bars, not seconds; prints, not book snapshots; one underlying (SPY, ^GSPC was not used); 59 events.
