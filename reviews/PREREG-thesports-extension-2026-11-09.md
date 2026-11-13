# TheSports pre-registration extension (Nick via coordinator, 9 Nov 00:57Z). Extends PR #213 / reviews/PREREG-thesports-2026-11-09.md, which stays unchanged.

Cutoff for everything below: events at or after **2026-11-09 02:00:00Z (epoch 1794189600)**. Committed before that time. Nothing here may be edited after commit; a change needs a new file and a new cutoff.

## Why
On pre-cutoff data the tennis rule T1 (quiet, point winner's token 0.40-0.60, buy at ask t+1.2 s, hold to resolution) earns +16.8c per share (23 matches, listed points), but a same-event placebo (same match and same side, shifted +-60-600 s, filters re-checked) earns +18.7c, so real minus same-event placebo is -1.9c (reviews/thesports-tennis-favourite-point-classes-2026-11-09.txt). The pooled placebo used in #213 is +2.1c. The two placebos answer different questions, so both are registered.

## Rule T1* (T1 with co-primary statistics)
Same event definition and filters as T1, events at/after the new cutoff, target N = 60 matches with at least one qualifying entry.
- Statistic A (pooled placebo, as in #213): equal-weight per-match mean of (real payoff - placebo payoff), placebo pooled per match. Command: `PREREG=1 PREREG_AFTER=1794189600 NPL=30 POINTS=1 CS2=cs2 DOTA=1 SIGNAL=1 TRADE=1 python3 live/thesports/big_events.py <slim dirs>` (T1 line).
- Statistic B (same-event placebo): per event, real payoff minus the mean payoff at its own shifted times (>=3 qualifying shifts required), averaged within match. Command: `FAVTEST=1 SPORTS=tennis PREREG_AFTER=1794189600 python3 live/thesports/event_sweep.py <slim dirs>`, line "ALL point messages | winner token 0.40-0.60".
- T1* passes only if BOTH statistics have a 90% match-clustered bootstrap CI entirely above 0. Its p-value for Holm is the larger of the two one-sided p-values.

## Rule U1 (tennis underdog, any in-play time)
- Hypothesis: the underdog is underpriced in play no matter when we enter (a price level mispricing, not a message-timing effect).
- Entry: for each tennis match with a Polymarket moneyline, every 60 s between its first and last TheSports message (+60 s inside both ends), for each of the two tokens: if mid is in [0.40, 0.50), spread <= 5c and ask < 0.99, buy 1 share at the ask 1 s later, hold to resolution (settle proxy: last mid >= 0.95 pays 1, <= 0.05 pays 0; unresolved excluded).
- Statistic: per-match mean payoff over that match's entries; benchmark 0 (fair price); 90% match-clustered bootstrap (2000 resamples).
- Target N = 60 matches with at least one entry. Command: `UNDERDOG=1 SPORTS=tennis PREREG_AFTER=1794189600 python3 live/thesports/event_sweep.py <slim dirs>`, line U1.

## Rule U2 (tennis underdog, first time in band)
- Same as U1 but only the first qualifying grid time per token per match; per-match mean over its (at most two) first entries.
- Same N, statistic and command (line U2). Purpose: whether a single timed entry captures what U1 earns.

## Multiple tests
Family of four rules: T1*, D1 (unchanged from #213), U1, U2. Holm correction at one-sided 0.05 (equivalent to the 90% two-sided CI). A rule that has not reached its N counts as p = 1. A rule is a success only if its Holm-adjusted p < 0.05 at its single evaluation. No interim tests (interim counts only, labelled not a test).

## Known pre-cutoff numbers (not a test, shown so the registration is honest)
U1 -5.3c per match (45 matches, CI [-12.6, +2.1]); U2 -9.7c per match (45 matches, CI [-14.9, -4.8]). The underdog gain seen in T1 pre-cutoff data is not present when entering at any time. Expect U1/U2 to fail.
