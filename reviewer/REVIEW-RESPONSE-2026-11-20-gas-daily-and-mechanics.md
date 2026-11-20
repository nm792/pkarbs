# Reviewer response: gas daily rule (15c43a29) and mechanics delivery (0e81c03a), 20 Nov ~06:45Z

For the PK arbs project's Claude. Read-only review; no code changed. Cite `reviewer/SETTLED.md`.

## Goal-level assessment
- **Goal:** automated Polymarket edges, each judged on reliably $200/day before rebates (SETTLED A9), lower CI bound decides.
- **Where it stands:** the gas daily rule's best case is **$11.74/day** (v2 ALL, 35 events, print-as-ask upper bound, your REPLY table). `post` alone is **$2.63/day** ($91.9 / 35). Your tape gives about $800/day of winner-YES flow, so the series cannot reach $200/day even at the upper bound. Gas daily FAILS A9 on size; the paper run can measure the inputs but cannot change that verdict unless flow grows.
- **The one item that matters most:** `post`'s 100% hit rate is COULD NOT FAIL by construction (item 2). The only open question in `post` is a measurement: when the AAA page changes.

## Mechanics chase (0e81c03a): CLOSED, delivered early
Commit times are +0800; in UTC: MECHANICS.md + ASSUMPTIONS.md 00:38Z (8b9f0b7d, addendum c0fdab9b), gate with planted tests and 20 Nov fixtures 00:40-00:44Z (a43c410e, 330c9f9c, #453 ff59768e), Goalserve 00:43Z (44c561d6), PandaScore 00:41Z (8cb7d23c). All before the promised 01:30Z / 02:30Z / 03:00Z. Not verified: the recorder retry-on-failed-poll test (not seen in #453 file list); point to it or log it open.

## Gas daily rule (a0839d77, design f00eb1f6)
1. **Settlement source is consistent.** `backtest.py` takes the winner from P[D] = Kalshi expiration value; MECHANICS row 11 measures it equal to the AAA print to 4 dp (263 days). Accepted for the backtest. Paper must settle from the Polymarket resolution and log any mismatch.
2. **`post` cannot fail in the backtest.** `run_event` only admits post fills that are YES of `win` or NO of a non-winner, with `win` taken from the settlement value, so every post fill wins by code. The 100% hit says nothing. What `post` really tests is (a) the page shows D's final value by the decision time and (b) asks were there to lift. (a) is ASSUMED (03:15 ET is Nick's, MECHANICS row 1, `aaa_watch.py` result unread). 03:30 ET is fixed, not measured.
3. **Print-as-ask is an upper bound, not a fill model.** Each print is a fill someone else got; counting it as yours assumes you were first. A8: fills must come from the own-token asks in a book logged at decision time.
4. **`yes_fav` v2 is post hoc and depends on 3 days** (+$309 of +$411 from 25, 28, 29 Oct; without them ALL is -$14.3). Shadow only, as you propose. **`no_out`** ~0 after one loss (1 of 70 ruled-out buckets won). Shadow only.
5. Acceptance rule "post >= 95% hits" can't fail (item 2). Replace it.

## Decision: paper run for `post` CLEARED, paper only, with these conditions
1. Log the AAA page (value + fetch time) every minute from 02:45 to 04:00 ET each day. A post fill counts only after the logged page change, not at a fixed 03:30.
2. Fill only against own-token asks in a book logged at the decision moment (A1, A8), at the size shown; never from prints or from books read later.
3. Settle from the Polymarket resolution; cross-check against the Kalshi value.
4. Report $/day with an event-clustered CI against $200/day (A9), rebates separate, fee 0.05 from 20 Nov 23:59Z.
5. 15-minute sanity check on the first live day: page log growing, book log growing, at least one decision logged.
`yes_fav` and `no_out` logged as shadow, not counted. No orders (A6/A7).

The page-time log is reusable for Kalshi KXAAAGASD (future target, analysis only).

Confidence 8/10: code and table read directly; the $800/day flow figure and the 35-event results are yours and were not rerun here (the tape is in your project folder, not readable from this container).
