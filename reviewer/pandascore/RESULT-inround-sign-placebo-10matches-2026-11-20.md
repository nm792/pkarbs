# RESULT (EXPLORATORY / UNCHECKED, PandaScore thread, 20 Nov 2026 09:30Z): in-round events vs Polymarket winner-market trade price, 10 matches
Spec: reviewer/pandascore/PREREG-inround-sign-placebo-2026-11-20.md (thresholds written before this run). Code: it/ps_inround_test.py. Data: scratch/ps_samples/ (IT P88x + P88z, box hours 19 Nov 11Z-22Z; match 1791311 is the truncated 882-message sample, not the full 3,214). Prices: public data-api v2 trades, outcome 0, last trade at or before the time. NOT audited by another thread; rule-to-code table NOT filled by another thread => UNCHECKED.

## Numbers (H = 15 s, events within 15 s of the last kept event of the same kind dropped)
| Event | n (event x market rows) | LEAD (mean signed move 0 to +15 s) | sign-perm p | ANTICIPATION (-15 s to 0) | p | matches with LEAD > 0 |
|---|---|---|---|---|---|---|
| Kill (opponent alive count drops) | 482 | +0.49c | 0.001 | +0.18c | 0.20 | 6 of 10 |
| Round end (team score rises) | 232 | +0.68c | <0.001 | +0.91c | 0.0002 | 10 of 10 (1 at 0.00) |
Per-match kill LEAD (c): 1789179 -0.21 (n14), 1789181 +0.87 (89), 1789182 -0.03 (107), 1791306 -0.05 (42), 1791309 +0.46 (49), 1791310 -0.48 (12), 1791311 +2.91 (14), 1796498 +0.33 (22), 1803639 +1.75 (30), 1803646 +0.48 (103).
Planted check (+3c injected 5 s after every kept event, same pipeline): kill LEAD +0.49c to +2.23c (recovers about 58% of the planted size), round end +0.68c to +1.33c. So the test detects a lead and has the right sign; it understates size, so a real kill LEAD may be nearer +0.85c than +0.49c.

## Verdict against the pre-registration: UNKNOWN (not a pass, not yet a fail)
- Kills: pooled LEAD +0.49c is below the +1.0c PASS threshold; 6/10 matches positive (below 70%); the sample has 10 matches (needs 12) though 482 rows exceed the 150 minimum. The p=0.001 is optimistic: rows are events x up to 3 markets of the same match, and events cluster. No anticipation (good for a lead claim), but the size is small.
- Round ends: ANTICIPATION +0.91c (p=0.0002) is larger than LEAD +0.68c: the price already moves in the round winner's direction in the 15 s BEFORE the PandaScore round-score message. This repeats the earlier interim finding (Polymarket first on round ends).
- Costs, as documented: taker fee 0.05*p*(1-p) = 1.25c per share at p=0.5, 1 s taker delay on these markets (secondsDelay 1). A kill lead of about 0.5c to 0.9c does not cover the 1.25c taker fee at mid prices. No edge after the fee on THIS evidence for taker orders; resting-order economics are untested (no ask depth in public trades).

## What would settle it
More matches (the capture restart; 12 matches minimum and more kills), own-book asks from the slim pmcs2 recorder at event times (replaces last-trade prices), and an independent audit with the rule-to-code table. Next live read of the capture is queued for the 09:11Z session.

## Update 16:05Z: 15 matches (P95 added 5 new matches; b7ed383e68)

Command: `python3 -I it/ps_inround_test.py scratch/ps_samples` and with plant `0.03`. Same script as above, unchanged.

- Kills (n=652 market-rows): LEAD +0.75c, p<0.0001 (optimistic: rows are not independent). ANTICIPATION +0.15c, p=0.20 (clean). 11 of 15 matches positive (73%). Largest: 1803648 +3.01c (n=38), 1791311 +2.91c (n=14, truncated), 1791312 +1.77c, 1803639 +1.75c. Negatives: 1791310 -0.48c, 1789179 -0.21c, 1791306 -0.05c, 1789182 -0.03c.
- Planted +3c: kills read +2.25c, so about 1.5c of the 3c came back (about 50%). Scaling the real +0.75c by that gives a true lead of maybe 1.5c, with wide error. Not yet above the 1.25c taker fee with any margin.
- Round end: LEAD +0.87c but ANTICIPATION +0.99c (p<0.0001): the price already moves before the score changes, so it is not a lead.
- Pre-registered verdict: UNKNOWN. Sample size now met (15 matches). LEAD +0.75c is below the +1.0c PASS bar and above the +0.5c FAIL bar. The rows-vs-events count of kept kills was not separately checked against the 150 bar here. The five new matches are mostly small or partial samples.
- Still UNCHECKED: no independent audit or rule-to-code table by another thread. Prices are last public trades, not each token's own book asks.
