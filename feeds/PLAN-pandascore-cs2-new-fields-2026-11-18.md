# PLAN: PandaScore CS2 new fields and round-score source (18 Nov 2026) — DRAFT, not locked

Cites feeds/STANDARD-feed-latency-test.md v1 (Nick-owned). Benchmark is the Polymarket price, never another feed. No deviation from STANDARD v1 is requested.

## Why
PandaScore (18 Nov, relayed by Nick) says CS2 now carries player economy, weapons, HP and a new "latency" field, that round score is typically their fastest data and player kills are slower, and that the trial is kept open. Our 16 Nov order-stable audit found no lead on CS2 round events (424 events, 10 matches, median -30.6 s, price after feed 11.7%). That used round score and player-alive flips only, and had no source label.

## What I do not know yet (settle by 18 Nov 12:00Z via IT note TO-IT-URGENT-pandascore-cs2-new-fields-check)
- Exact new field names and the shape of the latency field: the docs host is not reachable from my session. Nothing below uses a guessed name.
- Whether our stored payloads already hold the new fields. ll_capture.py stores the entire message as `payload` and `available_fields`, so they should be there if no opt-in is needed. Unverified until IT reads real files.

## Dates (UTC)
| When | What | Owner |
|---|---|---|
| 18 Nov 12:00Z | IT reply: updated docs committed, key inventory, available_fields by date, latency field examples, bytes per message | Prime Bot / IT |
| 18 Nov 15:00Z | Gap check: if new fields are missing from stored data, escalate the fix (opt-in or capture edit) as a new urgent IT issue, with a sample of 60 s of one live socket as proof | this thread |
| 18 Nov 18:00Z | PRE-REGISTRATION committed and locked (events, windows, strata, N, deadline), plus rule-to-code table | this thread writes; a different thread fills the table |
| 19 Nov 06:00Z | Planted-edge and no-edge discrimination check on synthetic data through the real parse path passes (a no-edge input must fail; a planted +5 s edge must pass) | different thread from the author |
| 19 Nov 00:00Z | Start of the test sample: every CS2 message with the new fields after the lock. Earlier data is exploration only, not scored | capture |
| 25 Nov | CS2 Major begins: Major matches go into the same sample, no restart of capture | IT |
| 30 Nov 12:00Z | ONE evaluation at the stated N. No peeking before | this thread |
| 1 Dec | Independent audit by a thread that did not run the test | audit thread |
| 2 Dec | Verdict to Nick. Trial end date is unconfirmed (earlier note: 1 Dec; PandaScore says it is kept open). I will ask Nick to confirm the end date with PandaScore | Nick |

## Hypotheses to lock (drafts)
- H1 (primary): round-win events whose latency label shows the fast (score) source lead the PM price. Events as in STANDARD section 2, receive time on the shared host clock, onset = first mid move of at least 2c in the event direction inside -60/+60 s, placebo = 10 random event-free times in the same match.
- H2: player-death events (alive flips, with HP/economy context) lead the price. Expected weaker, since PandaScore says kills are delayed.
- H3: bomb-planted events, only if `bomb` is in `available_fields` at the time.
- Economy and weapons are covariates for H1/H2 (for example man-advantage and buy state), not events. They are not tested as lead events.
- Strata: volume below / at or above $25k, as in STANDARD v1 (only if each has n >= 30; else "unknown, settled by <what, when>").
- Bar for each: STANDARD section 3 (n >= 30 per stratum, median real-minus-placebo >= +2.0 s, match-bootstrap 95% CI excluding 0, price after feed in >= 60%). Three hypotheses = a family: the lock states a correction for the count (Bonferroni across H1-H3 at the CI level) before data.
- No silent defaults: events missing a latency label, field or PM price rows are excluded and counted in the report.
- Money bar (STANDARD section 5) only if section 3 passes; every cost term sourced in a cost table first.

## Sample size
CS2 produced about 42 round events per match in the earlier set, so n >= 30 events is cheap. The binding limit is the number of matches for the match-bootstrap and the two volume strata. If fewer than about 10 matches per stratum exist by 30 Nov, the stratum is reported as unknown. I will post the match count per stratum on 24 Nov (a count, not a result).

Confidence 7/10: dates and structure are sound; field names, trial end date and the volume-strata match counts are open items until IT replies.
