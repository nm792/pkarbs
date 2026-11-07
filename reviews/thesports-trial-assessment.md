# TheSports trial: running assessment

Started 2026-11-07 (Nick, 07:38Z: "we need to assess this trial properly so keep the records"). Update after every new result. Newest result first inside each section.
All lead and timing figures are quoted next to a random-time placebo. Anything not proven is marked UNKNOWN with what would settle it.

## Trial facts
- Access: basketball, tennis, esports topics (`thesports/{basketball,tennis,lol,dota2,csgo}/match/v1`, MQTT). LoL delivery began later (~02:50Z 7 Nov, 4,211 msgs); cricket not activated (Nick emailed account manager 02:53Z).
- Capture: Hermes server, from 15:50Z 6 Nov. Raw TheSports messages and Polymarket (PM) books recorded on the SAME logger and clock. Book receive time minus PM server timestamp: median 0.17 s (p90 0.8 s, n=2,838, first chunk).
- TheSports tennis payload has only `id` and `timeline`: no own timestamp, so TheSports' internal latency cannot be separated from ours. CS2 `timer` is the round-start epoch, not an event time.
- PM facts: `seconds_delay` = 1 s on tennis/CS2/LoL game markets. Typical spread 1c.
- Data analysed: `rn1/scores/thesports/final-topics-8917-slim/` (to ~02:50Z 7 Nov); newer chunk `slim-0517-32295` and tonight's LoL not yet analysed.

## Records policy (Nick 07:38Z)
Keep ALL raw TheSports and PM book captures for the whole trial; delete nothing. Hermes keeps exporting and committing the slim export (`live/thesports/export_slim.py`), raw to /vol2 + storage box per the server charter (no raw data on root disk).

## Method (shared by all sports)
Event = feed message showing a new score/event (history in a match's first message skipped). Sides from team names (diary names to PM outcome names; doubles by surname set), never from price co-movement. Fav token = the side the event favours. Price band 25-75%, spread <=3c. Taker net = bid at +h minus ask at t+0.2+1.0 s (1 s PM delay). Placebo = same events shifted by a random 60-600 s with the same side. Bootstrap over games. Half-move time = first second the favourable mid has gone half of its move (events with >=3c total move).
Scripts: `live/thesports/` : `event_price_change_names.py` (name bridge), `tennis_break_test.py`, `big_events.py` (`CHECK=1`, `POINTS=1`, `LAG=1` blocks), `simple_ladder.py`, `audit_mapping.py`, `export_slim.py`.

## Tennis (28 name-verified matches, 5,835 live points)
- **Size of event moves (60 s before to 60 s after, unfiltered):** break +7.0c median (n=106, 86% >=3c); break that wins the set +6.0c (n=20); hold at 5+ games +2.0c (n=86). Markets are all match-winner (moneyline).
- **Timing vs price:** price reaches half its move a median 14-15 s BEFORE the TheSports point message (10-90%: -23 to -6 s; break points, n=64 / saves n=48 / other points n=478). Placebo -8 to -12 s (the placebo is biased negative because the window ends at +10 s, so the real excess lead is about 2-7 s, and real events are tighter and far more often big: 40% vs 10% at break points).
- **Net after spread and 1 s delay (taker, no feed-first filter):** about -1c at +10 s and +30 s for break-point-created, saved, and other points; real minus placebo inside the 90% interval except "other points" at +10 s (+0.07 to +0.18c, not tradeable). Game-end (break) net also about -1c, real = placebo.
- **Reference:** TheSports shows each game score a median 15 s BEFORE Polymarket's own sports-ws score (10-90%: -50 to +3 s; 20 matches, 357 changes). So TheSports is ahead of PM's score feed but behind the PM price.
- **Verdict:** no edge from TheSports tennis (price already moved, real = placebo). Whether any faster feed beats the price: UNKNOWN, settled by timing a second feed (LSports trial, deferred to next week) on the same clock. The 14 s gap may be the price source being faster than TheSports, not TheSports being slow versus its own claim (2-3 s vs officials).
- Not done: Sofascore reference (no per-point timestamps expected); per-point topic (none in our five topics).

## Tennis: official start/end time check (Nick 07:42Z) - NOT POSSIBLE with what we can reach
- **Sofascore** (startTimestamp/endTimestamp): `api.sofascore.com` returns HTTP 403 from the cloud container directly AND through TinyFish. Not obtained. Also expected to give start, not a match-point timestamp; its point-by-point has no times. Hermes' server IP not yet tried (task for Hermes).
- **TheSports diary** has `match_time` (scheduled start) and `updated_at`, but `updated_at` is a median ~8 h AFTER our last game message (post-match edits), so it is not an end time. Unusable.
- What the capture alone shows (26 ended, name-paired matches, all on one clock; NOT official times):
  - Polymarket sports-ws "ended" flag arrives a median +32.7 s AFTER TheSports' last game-result message (10-90%: +2 to +71 s, n=19). TheSports is ahead of PM's own score feed at match end too, as at game level (-15 s).
  - Winner's price stays >=98.5% from a median 59 s BEFORE TheSports' last game-result message (10-90%: 336 to 11 s before, n=18). This is NOT a match-point timestamp: lopsided matches are near 99% before the last point, so it cannot be used as the end time.
- **Other sources tried 7 Nov 07:50Z:** ESPN scoreboard (`site.api.espn.com/.../tennis/{atp,wta}/scoreboard?dates=`) works and lists 103 ATP / 207 WTA competitions for 6 Nov, but gives only a minute-resolution `startDate` and a final status, no end time and no points. Flashscore (via TinyFish) returns only a gambling-notice shell. ATP Tour (via TinyFish) returns a daily schedule with "Starts at"/"Not before" times only. None gives a match-point timestamp. Hermes task written: `agent/tasks/TASK-tennis-reference-times-2026-11-07.md` (Sofascore from the server IP, 28 matches listed in `rn1/scores/thesports/reference/tennis-matches-28.csv`).
- A true ground truth needs a live recording of a timestamped source during a match. Not yet set up.
- **Verdict: UNKNOWN** whether TheSports or the price is "late" against true event time. Settled by: an independent timestamped source for the same matches (Sofascore via Hermes, or a live recording of one match with a visible clock).

## CS2 (5 name-verified maps; 112 round-win events)
- Round wins by stage, favourable move t-10..t+30: early/mid 0.0c median (13% >=3c, n=45 priced), loser>=10 -0.3c (25%, n=12), winner reaching 12 +0.5c (0%, n=3). Net about -1c at +5/+10/+30 s, real = placebo (CI wide, 5 maps).
- Timing: 112 events too few; half-move timing with the 1 s window NOT yet run for CS2. Earlier median lead +12.8 s vs placebo +3.6 s (91 events) used the asymmetric window and is NOT reliable.
- **Verdict: UNKNOWN** (5 maps). Settled by: more maps (new chunk, 25 Nov Major) and the half-move timing run.

## LoL
- 3 games, market paired by sign-free price co-movement, side by home.side (verified 3/3). Type 2/3/4 events inferred as tower/inhibitor/monster from counts (TheSports does not document codes).
- Priced events: 6 towers, 5 monsters, 0 inhibitors. Earlier kill lead +4.2 s vs placebo -0.2 s (25 events, one series).
- DK-BLG dry run (6 Nov, 1 match, 38 kills): PM score feed median 17.6 s after price; 62 paper bids, 0 fills.
- **Verdict: UNKNOWN.** Settled by: tonight's second LoL semi and more series; TheSports documenting event type codes; LoL HTTP authorization.

## Dota 2
Capture delivering; not timed. BLAST from 17 Nov.

## Basketball
Dropped from review by Nick (04:39Z). Only record: TheSports a median 2.5 s after the PM price (35% first).

## Withdrawn results (kept for the record)
| Result | Why withdrawn |
|---|---|
| "TheSports leads Polymarket tennis" (70% first, +7.8 s median) | Window artefact: random-time placebo +7.5 s, 73% first. |
| CS2 +25c/map and other TheSports $ results | Side bias from price-paired sides; wrong-side placebo -11c. |
| -7c net on first LoL/CS2 cut | Thin-book outliers; fixed with spread <=3c and medians. |
| Settlement-based side test | Hold-to-resolution on "scoring team" is positive at random times. |
| Market-2.5% resting bid (-$0.04/share, 164 fills) | Fills only when the signal is wrong (adverse selection). |
| "Big events leave nothing to trade" (-1c, median move 0-0.5c) | Window started at t-10 s and the feed-first filter kept events the market ignored. Replaced by the unfiltered result above (breaks move ~7c, but before the message). |
| "Price moves at least 30 s before TheSports" | A -30..0 s bucket cannot say that; 1 s binning gives about 14 s. |
| "Re-run once team names" / "74% before half" | Superseded by name-verified sides. |

## Open items
0. 7 Nov 09:15Z: newer chunk `slim-0517-32295` (04:00-05:08Z; 6,362 CS2, 4,939 tennis msgs, no LoL) cannot be tested: its books/markets cover only 12 tennis moneyline markets (18 tokens), no CS2 markets, and none of them is a match with TheSports events (0 name pairs). Hermes diagnosis (outbox 09:19Z): discovery filter `MKT_TYPES` + live window found only 12 tennis moneyline markets; checked against the code and chunk 8917: `child_moneyline` (CS2 map winners) IS included already, so likely no CS2/LoL/Dota market was in the live window then. No capture edit needed. Waiting for the next chunk with live CS2/LoL books.
1. LoL tonight and new CS2 maps: rerun `big_events.py` on the new chunk and add half-move timing for CS2/LoL.
2. Ask TheSports for a per-event timestamp or a faster tennis/esports product.
3. LSports trial timing vs price on the same clock (deferred to next week).
4. Dota 2 timing once events are available.
