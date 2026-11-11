# TheSports pre-registered rules (Nick's request via coordinator, 9 Nov 00:28Z)

Committed before the cutoff. Only events at or after **2026-11-09 01:00:00Z** (epoch 1794186000) count. Nothing below may be edited after commit; a new rule needs a new file and a new cutoff.

## Rule T1 (tennis)
- Event: a TheSports tennis point message; favourable side = the side that won the point.
- Filter: price quiet (|favourable mid move over t-30..t| < 1c); favourable mid at t-30 in [0.40, 0.60).
- Action: buy 1 share of the favourable token at the best ask at t + 0.2 s + 1.0 s (our latency + Polymarket sports delay); hold to resolution (settle proxy: last mid >= 0.95 pays 1, <= 0.05 pays 0; unresolved games excluded).
- Statistic: mean over matches of (payoff real - payoff at placebo times), placebo = same events shifted +-60-600 s, 30 shifts per event, same filters re-checked at the shifted time.
- Test: ONE evaluation when 60 post-cutoff matches have at least one qualifying entry. Success = 90% match-clustered bootstrap CI for real - placebo entirely above 0 (1500 resamples). No interim tests, no look-ahead, no multiple-test penalty because it is the only tennis rule.
- Power: per-match sd of the difference 28.7c (from pre-cutoff data); 60 matches gives ~80% power for a true +10c.

## Rule D1 (Dota 2)
- Event: a TheSports Dota kill message; favourable side = the killing team.
- Filter: quiet as above; favourable mid at t-30 in [0.60, 0.90).
- Action: buy 1 share at the best ask at t + 1.2 s; value at the mid price 60 s after that landing (no exit cost; spread paid on entry).
- Statistic and test: same as T1 clustered by game; ONE evaluation at 40 post-cutoff games with at least one qualifying entry.

## Code and how to run
`NPL=30 POINTS=1 CS2=cs2 DOTA=1 SIGNAL=1 TRADE=1 PREREG=1 PREREG_AFTER=1794186000 python3 live/thesports/big_events.py <slim dirs pooled>` (block "PRE-REGISTERED RULES" at the end of live/thesports/big_events.py). Interim counts may be printed with PREREG_INTERIM=1 and are labelled not a test.
