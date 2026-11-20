# PRE-REGISTRATION: PandaScore CS2 in-round events vs Polymarket winner-market price (draft 20 Nov 2026 ~04:30Z, PandaScore thread, for the Reviewer)
Status: EXPLORATORY draft. Written BEFORE the all-matches run; the 3-match look (n=66 kills, 29 round ends, it/ps_inround_test.py, e4196c2449+) is NOT used to set any threshold below.
Not the same test as feeds/PREREG-pandascore-cs2-latency-sequential-2026-11-18.md (round-score events, lat0 series); that one stays as registered.

## Question
After a PandaScore in-round event message is received, does the public Polymarket price of the winner market move in the direction the event favours, beyond chance, and is that move NOT already in the price in the 15 s before the message?

## Data
- Feed: `scratch/ps_samples/` exports of the raw capture (whole payloads, `recv_ns` = our receive time), every CS2 match since 19 Nov 11:20Z with in-round fields (`available_fields` includes player_alive). Matches with <30 public trades on the market are excluded before looking at results.
- Prices: public trades from data-api v2 `/trades?condition=<id>` (cursor paging), outcome_index 0, last trade price at or before time t. Markets: match winner (BO) and Map N winner where N = PandaScore map_id at the event. Excluded: totals, handicaps, O/U.
- Direction s: +1 if the event favours the outcome-0 team. Kill: the opponent's alive count drops within the same round number. Round end: the team's score rises within the same map_id. Bomb events: unsigned descriptive only (side/plant direction ambiguous).
- Clustering: events of the same kind within 15 s of the previous kept event are dropped.

## Statistics (all pre-set)
1. LEAD = mean over kept events of s*(P(t+15 s) - P(t)). ANTICIPATION = mean of s*(P(t) - P(t-15 s)).
2. Sign test: flip s at random 5,000 times; p = share of |mean| >= observed (two-sided). Same for ANTICIPATION.
3. Placebo: same number of random event-free times per match (>=10 s from any event), random sign; LEAD placebo mean must be inside +-0.5c.
4. Unit check: per-match mean LEAD, and the number of matches with positive LEAD.

## Pass / fail
PASS (worth a latency probe): kills pooled LEAD >= +1.0c, p < 0.01, ANTICIPATION p > 0.05 (not already priced), >= 70% of matches positive, at least 12 matches and 150 kept kill events, placebo inside +-0.5c.
FAIL: LEAD < +0.5c or p > 0.10 at the same sample size. Otherwise UNKNOWN with what would settle it (more matches, own-book asks).
Costs: no P&L claimed here. A PASS only licenses the next step: both-token book recorder at the event times, taker fee 0.05*p*(1-p), 1 s taker delay, and a depth check.

## Known weaknesses (declared up front)
- Public trades are not the book: no ask depth; trade timestamps are whole seconds; staleness bias at thin markets (we require >= 30 trades).
- Kills cluster inside rounds, so events are not independent; the sign test treats them as independent (p is optimistic); per-match means are the check.
- Kill direction is not weighted by who died (star player, economy); round momentum may drift prices in the same direction as kills.
- PandaScore receive time includes our network path; Polymarket 1 s taker delay is not subtracted.

## Code
it/ps_inround_test.py (this spec), it/ps_chart_samples.py (eyeball), it/ps_export_samples.py (export). Independent audit required before any PASS is relayed (Reviewer rule); planted-lead check to be run by injecting a synthetic +3c move after kills into a copy of the price series and confirming LEAD detects it.

## Planted-lead check (coded 20 Nov ~04:45Z)
`python3 -I it/ps_inround_test.py SAMPLEDIR 0.03` injects a synthetic +3c move in the event direction 5 s after every kept event (undone at +16 s) and reruns the same pipeline. On the 3-match sample: kill LEAD rose from +1.52c (p=0.075) to +3.17c (p=0.0002), round end from +1.33c to +2.68c. So the test DETECTS a planted lead and the sign is right, but it recovers only about 55% of the planted size for kills (+1.65c of +3c): overlapping events and the undo trades blunt it. Read any real LEAD as a floor, not the size. A real run must show the same planted check on the full sample before a verdict.
