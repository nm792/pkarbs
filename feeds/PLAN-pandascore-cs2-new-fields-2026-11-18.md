# PLAN v2: PandaScore CS2 new fields and round-score source (18 Nov 2026) — DRAFT, not locked

Cites feeds/STANDARD-feed-latency-test.md v1 (Nick-owned). Benchmark is always the Polymarket price. v2 replaces the single 30 Nov evaluation (Nick's rule via coordinator, 18 Nov 08:21Z: a week is too late) with the daily sequential-look design the Goalserve test uses (feeds/PREREG-goalserve-odds-vs-pm-v2-2026-11-18.md, V12 to V23).

## DEVIATION REQUEST from STANDARD v1 section 3 and section 4 (needs Nick's approval before any scored data is read)
Section 3 says one evaluation at the stated N with a bootstrap CI. A daily look needs a stopping boundary instead. Deviation: the CI condition (bar 3) is replaced by the boundary below. Bars 1, 2 and 4 (n >= 30 events, median real-minus-placebo >= +2.0 s, price after feed in >= 60%) stay exactly as in STANDARD v1. No other change. Nick approves or rejects on a card before the lock.

## Why
PandaScore (18 Nov, via Nick) says CS2 now carries player economy, weapons, HP and a new "latency" field; round score is typically their fastest data and kills are slower; trial kept open. Our 16 Nov order-stable audit: no lead on CS2 round events (424 events, 10 matches, median -30.6 s, price after feed 11.7%), no source label.

## Open facts (IT issue #413, due 18 Nov 12:00Z)
- Exact new field names and latency-field shape. The docs host was allowed in this session's network settings at 08:23Z, but my fetch of the page was refused by the session's permission classifier, so I have NOT read it. IT downloads it instead.
- Whether stored payloads already hold the new fields (ll_capture.py stores the whole message plus `available_fields`, so they should, unless an opt-in is needed). Unverified.
Nothing below uses a guessed field name.

## Design (draft; locked in the PREREG file by 18 Nov 18:00Z)
- Sample: only CS2 messages received from 2026-11-19T00:00Z. Earlier data is exploration, never scored. First look on 20 Nov (about 01:00Z) on 19 Nov data, then one look per complete UTC day. Last look 30 Nov, or the day before the trial ends if PandaScore ends it earlier. One pass is audited and stands; a later look never overturns it.
- H1 (the only hypothesis that can be called a pass; alpha spent on it alone): round-win events whose latency label shows the fast (score) source lead the PM price. Event, receive time, onset (>= 2c in the event direction within -60 s/+60 s) and placebo (10 random event-free times in the same match) exactly as STANDARD v1 section 2.
- H2 (player deaths, with HP and economy as covariates) and H3 (bomb planted, only when `bomb` is in `available_fields`): informational only, no alpha, never relayed as a pass.
- Statistic: per match, mean of (real lead minus placebo lead) over usable events; t-statistic of the per-match means. Boundary as Goalserve V17: z_eq x sqrt(t) >= 2.60 with information time t = matches used / N_MAX, giving one-sided alpha 0.0093 for the cell under any look schedule. N_MAX = 60 matches (draft; fixed from the 10-match, 424-event history and Major coverage, to be confirmed by the null simulation). Same boundary on the negative side = "PM moved first" (a relayed verdict, error budget stated as in Goalserve V23).
- Pass = boundary met AND median real-minus-placebo >= +2.0 s AND price after feed in >= 60% AND n >= 30 events, per volume stratum where reported (below / at or above $25k). A stratum with fewer than 30 events is "unknown, settled by <what, when>".
- Daily checks before a look counts: planted-edge test through the real parse path on that day's data (a +3 s shift of PM rows must be recovered within 5%, a no-edge input must not pass), null simulation of the whole schedule at this accrual (reuse feeds/null_sim_20k.py design), completeness rule (every hour file present and `gzip -t` clean, poll log covers the day, as Goalserve V21), no silent defaults: events with no latency label or no PM price rows are excluded and counted.
- Every look is UNCHECKED until a thread other than the author signs the rule-to-code table and hand-checks the first 20 events; independent audit before any pass or fail is relayed to Nick.
- Money bar (STANDARD section 5) only after a pass; cost table sourced first.

## Dates (UTC)
| When | What | Owner |
|---|---|---|
| 18 Nov 12:00Z | IT reply on #413: docs committed, key inventory, available_fields by date, latency examples, bytes per message | Prime Bot / IT |
| 18 Nov 15:00Z | Gap check: fix escalated if new fields are missing | this thread |
| 18 Nov 18:00Z | Nick's deviation decision, then PREREG locked + rule-to-code table started by another thread | Nick / this thread |
| 19 Nov 00:00Z | Scored sample starts | capture |
| 19 Nov 23:00Z | Validation before first look: rule-to-code table signed, null simulation and plants pass | other thread |
| 20 Nov ~01:00Z | Look 1 (19 Nov data); daily after 00:30Z | IT, this thread reads |
| 24 Nov | Match count per stratum posted (a count, not a result) | this thread |
| 25 Nov | CS2 Major begins; no capture restart | IT |
| 30 Nov | Last look (or trial end if earlier). Trial end unconfirmed: earlier note 1 Dec, PandaScore says kept open | Nick to confirm with PandaScore |
| next day | Independent audit; verdict to Nick the day after | audit thread |

Earliest result: a pass needs about 20 matches at t = 0.33 and z_eq >= 4.5, so a clear edge could land by 22 to 24 Nov, before the Major. A weaker edge needs the Major's matches. Estimate, not measured.

Confidence 7/10: design and dates follow the Goalserve template and are consistent with STANDARD v1; open until field names, N_MAX, the trial end date and Nick's deviation approval are settled.
