# Result: metals fade / Brent follow around the Sunday reopen, out of sample (rule: LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md, merged in PR #365 before any number)

Net = gross - 2 x (9 bp fee + stressed half-spread: 1.0 silver/Brent, 4.9 copper, 6.2 platinum). Weekend-cluster bootstrap 95% CI. Script and cells: followups-2026-11-16/oos.py.

| Sample | Group | n signals | weekends | Gross bp | Net bp | Net 95% CI | weekends with right sign |
|---|---|---|---|---|---|---|---|
| Discovery, 1 h candles (already seen) | metals | 35 | 23 | +43 | +17 | -10 to +46 | 78% |
| Discovery rebuilt on 4 h candles | metals | 36 | 20 | +76 | +50 | +26 to +76 | 85% |
| **HELD-OUT, 4 h, before 22 Apr** | **metals** | **25** | **14** | **+27** | **+2** | **-84 to +104** | **43%** |
| held-out | silver | 11 | 11 | -25 | -45 | -159 to +120 | 27% |
| held-out | copper | 9 | 9 | +99 | +71 | -8 to +167 | 78% |
| held-out | platinum | 5 | 5 | +15 | -16 | -135 to +142 | 40% |
| Discovery 1 h | Brent follow | 22 | 22 | +7 | -13 | -50 to +23 | 50% |
| Discovery 4 h | Brent follow | 24 | 24 | -17 | -37 | -87 to +12 | 42% |
| **HELD-OUT** | **Brent follow** | **7** | **7** | **+46** | **+26** | **-269 to +397** | **57%** |

Rule outcome: H-metals NOT PASSED on the held-out sample (CI includes 0, only 43% of weekends have the right sign, silver goes the wrong way). Not a FAIL either: gross is positive and the interval is very wide, so it is unknown. H-brent: n = 7 < 8, so unknown; on the 22+24 discovery signals the trade as defined (exit 1 h after the reopen) does not earn anything, so the earlier "+48 bp" was a gap measure to the open price, not a tradable profit.
Two warnings. (1) The same 30 discovery weekends give +17 bp net on 1 h candles and +50 bp on 4 h candles: the size of the pattern depends on the candle resolution (staleness of entry and length of hold), which is a sign of fragility, not of a real effect. (2) Only copper keeps a positive held-out sign with a CI near zero (+71 net, n = 9); it is the thinnest book.
Sensitivity (4.5 bp fee instead of 9): held-out metals net +11 bp, CI -74 to +113, same conclusion.

## Capacity (live book 16 Nov ~15:30Z, per side)
Fillable within 5 bp: silver about $1.0-1.2M (about 0.9% of its $125M open interest), copper about $18-21k (OI $6.7M), platinum about $20-46k (OI $5M), Brent about $340-360k. Signals per weekend: silver 0.4, copper 0.4, platinum 0.3, Brent 0.7 (discovery rates). Even if the discovery net profit were real, an upper bound is about $440/week from silver at full 5 bp size, about $20/week from copper and about $10/week from platinum. That is far below the $500/day target, and silver, the only one with size, has the wrong sign out of sample.
Limits: 4 h candles for the held-out weekends (entry and exit staleness up to several hours), live spreads from one Monday snapshot, fee assumption not confirmed for xyz, 7 Brent held-out weekends only.
Next: forward test from 21-23 Nov needs the live logger to record these symbols (TASK-weekend-perps-metals-logger-2026-11-16.md).
