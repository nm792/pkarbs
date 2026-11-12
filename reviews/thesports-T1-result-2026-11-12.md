# TheSports T1 (tennis) pre-registered test result, 12 November 2026

Rule: reviews/PREREG-thesports-2026-11-09.md (cutoff 2026-11-09 01:00Z). Data: final-topics-32295-slim + final-topics-32295b-slim, export f80025b293 (ts_mqtt to about 23:00Z on 11 November; markets 2,773 rows).
Command: `NPL=30 POINTS=1 CS2=cs2 DOTA=1 SIGNAL=1 TRADE=1 PREREG=1 PREREG_AFTER=1794186000 python3 big_events.py slim-1102-32295:final-topics-32295-slim:final-topics-32295b-slim` (run in rn1/scores/thesports).

## Verdict: first 60 qualifying matches by time of first qualifying event
The locked rules and parameters are unchanged. A copy of big_events.py adds one data filter, enabled by FIRSTN=60: after `R, P = trade_events(L2, band)` for rule T1 it keeps the first FIRSTN qualifying matches by earliest qualifying-event time (last kept match 2026-11-11 07:20Z, 60 of 69) and drops the rest from R and P.

- 60 matches, 189 entries
- real -3.43c, placebo +0.13c (n17120)
- diff 90% match-clustered CI [-9.96, +3.35], p=0.451
- Success rule (whole CI above 0): FAILS

## Secondary: all 69 matches (unmodified locked script)
- 69 matches, 211 entries
- real -3.80c, placebo +0.92c (n23014)
- diff 90% CI [-11.23, +2.10], p=0.280
- Success rule: FAILS

Both agree. Note: 60 matches had about 80% power for a true +10c (PREREG). The result does not support an edge; it does not prove there is none. Not yet independently audited.

## Dota D1
39 of 40 games, not evaluated (no peeking).

## Note
An earlier first attempt at the all-69 run was killed (out of memory when two runs overlapped); it printed no result. Counts at 03:15Z: T1 69/60, D1 39/40.
