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
- **Replication on new matches (chunk slim-1102-32295, 9 name-paired matches, 1,355 live points, 7 Nov 04:00-13:15Z):** breaks +5.0c median over -60..+60 s (n=27, 77% >=3c); price half-move median -16 s before the feed message for break-point-created (n=15, 100% before) and -16 s for other big moves, placebo -7 to -12 s; net taker -1.0c at +10 s (break-point-created -1.8c, 90% CI of real minus placebo [-0.93, -0.48], i.e. worse than random) and +30 s. TheSports vs PM sports-ws: median -15.9 s (4 matches, 61 changes). Same picture as the first 28 matches.
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

## CS2 (10 name-verified maps, 196 round wins; earlier chunk 5 maps / 112 events)
**Status: earlier conclusion "no edge, rounds barely move the price" WITHDRAWN (Nick 13:18Z, audit 13:40Z).** It came from 5 bins of medians and a feed-first/band filter that hid a gradual move. Corrected reading below. Profit: UNKNOWN.
- **Pairing audit (`live/thesports/cs2_audit.py`):** all 10 are the correct map-winner markets ("Map N Winner", `child_moneyline`, N = TheSports box_num), names verified. Book activity: 700-6,500 rows per map, 170-930 price changes per map (about one every 10-15 s); median spread 1c on 8 maps, 9-10c on the Johnny Speeds vs Drama map (thin). Side check: c_score-derived round winner gives +3.0c signed move, positive as expected.
- **Round winner's price, mean signed move over -90..+60 s around the c_score message (10-90% band): real +4.4c (n=124) vs random-time placebo +0.02c (n=357).** Where it happens: -90..-60 s +1.3c, -60..-30 +1.8c, -30..-15 +1.3c, -15..0 +0.1c, 0..+15 -0.6c, +15..+60 +0.2c (placebo ~0.1-0.3c in every bin). So a round win moves the price about 4c, and the price has finished moving about 15 s BEFORE TheSports' message.
- **Net taker (buy ask +1.2 s, sell bid +10/+30 s, spread<=3c, no feed-first filter):** -1.2c / -1.6c vs placebo -1.5c / -0.8c: nothing left after the message. Consistent with the feed being >=15 s late; a faster feed could capture part of ~4c per round, but this is UNKNOWN until a faster feed is timed on the same clock.
- **"Only 2 priced map-point events" explained:** the test keeps pre-event price 25-75%; at a map point (winner at 12 of 13) the leader is already >75%, so most map points fall outside the band. Not a pairing fault. Map-point/overtime economics: UNKNOWN (needs a wider band and more maps).
- **Other TheSports CS2 event types** (`event` typeid 8 kill, 2 round end, 6 alive counts, 4/5 bomb): the round-end event arrives with the c_score change (median -0.5 s), so it is no faster. Kill/typeid-2 side mapping via `home.side` disagrees with the c_score side in 15% of rounds (side swaps at half-time?), so kill-level results are NOT trusted yet (kills show about 0c after the message either way).
- Earlier CS2 "+12.8 s vs placebo +3.6 s" and "+25c" stay withdrawn.

## LoL
- 3 games, market paired by sign-free price co-movement, side by home.side (verified 3/3). Type 2/3/4 events inferred as tower/inhibitor/monster from counts (TheSports does not document codes).
- Priced events: 6 towers, 5 monsters, 0 inhibitors. Earlier kill lead +4.2 s vs placebo -0.2 s (25 events, one series).
- DK-BLG dry run (6 Nov, 1 match, 38 kills): PM score feed median 17.6 s after price; 62 paper bids, 0 fills.
- **Verdict: UNKNOWN.** Settled by: tonight's second LoL semi and more series; TheSports documenting event type codes; LoL HTTP authorization.

## Dota 2 (first read 7 Nov 15:10Z; 4 Game-1 winner markets paired by names, 86 kill events; Hermes already records books for live Dota Game-N-Winner markets, 15 markets from 5 series in chunk slim-1102-32295)
- Message format: no `event` list; per-team `stats` (inferred: [0]=kills, [1]=11-bit tower-alive mask, [2]=6-bit barracks mask, [3]=net worth), `roushan_timer`. Events are derived from changes between messages; the stats meaning is INFERRED, not documented by TheSports.
- **Kills (n=86, 4 games, band 10-90%):** winner side's price, mean signed move: before message (-90..0 s) about +0.7c in total, after message (0..+60 s) +1.3c (+0.86 in 0..15 s, +0.44 in 15..60 s); placebo after message -0.06c. Half-move time (events with a >=3c move, n=23 of 86): real median -2 s (10-90%: -24 to +4) vs random-time placebo -15 s (-28 to +4, n=73): the price moves around/after the kill message, not clearly before it. This is the first sport where the placebo comparison favours TheSports on timing.
- **Net taker (buy ask +1.2 s, sell bid +10/+30 s, spread<=3c, 10-90%, no feed-first filter):** +10 s real -1.32c (n=22) vs placebo -2.09c, diff 90% CI [+0.10, +1.56]; +30 s real -1.91c vs placebo -2.31c, diff CI [-0.45, +1.59]. Both still negative after spread: no profit shown. Spreads are wider than CS2 (median 2-4c).
- Towers (n=28) and barracks (n=4): too few; UNKNOWN. Roshan: 1 timer start, UNKNOWN.
- **Verdict: UNKNOWN, weak sign of a timing lead on kills; no profit.** Settled by: more Dota games (BLAST Slam from 17 Nov, DreamLeague), TheSports field documentation, and Game 2/3 markets.

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
| CS2 "round wins barely move the price, no edge" (10 maps) | Medians of narrow bins and a band filter hid a gradual ~4c move that completes before the message; replaced by the CS2 section above. |

## Open items
00. 7 Nov 13:10Z: books_mid for slim-1102-32295 landed (800,150 rows); tennis and CS2 run on it (above). LoL still 0 messages.
0. 7 Nov 09:15Z: newer chunk `slim-0517-32295` (04:00-05:08Z; 6,362 CS2, 4,939 tennis msgs, no LoL) cannot be tested: its books/markets cover only 12 tennis moneyline markets (18 tokens), no CS2 markets, and none of them is a match with TheSports events (0 name pairs). Hermes diagnosis (outbox 09:19Z): discovery filter `MKT_TYPES` + live window found only 12 tennis moneyline markets; checked against the code and chunk 8917: `child_moneyline` (CS2 map winners) IS included already, so likely no CS2/LoL/Dota market was in the live window then. No capture edit needed. Waiting for the next chunk with live CS2/LoL books.
1. LoL tonight and new CS2 maps: rerun `big_events.py` on the new chunk and add half-move timing for CS2/LoL.
2. Ask TheSports for a per-event timestamp or a faster tennis/esports product.
3. LSports trial timing vs price on the same clock (deferred to next week).
4. Dota 2 timing once events are available.

## Update 8 Nov 01:30Z: gap slim 14:00-16:00Z (capture was down 16:00Z to 00:21Z, restarted with Nick's approval)

Data: `rn1/scores/thesports/final-topics-32295-slim` (books_mid 420,817 rows, ts_mqtt 261,695 msgs). Coverage gap: the stretch after `slim-1102-32295` ended (~13:15Z) up to 14:00Z is not in either slim; asked Hermes only if it matters. Run: `CS2=cs2 POINTS=1 CHECK=1 LAG=1 DOTA=1 python3 live/thesports/big_events.py <slim>`. Raw output kept in the PR description summary, same method as above (random-time placebo beside every figure).

| Sport | Events | Price half-move vs message (real / placebo) | Net taker +10 s (real / placebo, 90% CI of diff) | Verdict |
|---|---|---|---|---|
| Tennis | 27 matches, 13 paired, 1,428 points | median -14 s / -11 s (break-point points -15 s / -9 s) | -0.97c / -1.09c (-0.04..+0.25) | price moves first; no profit |
| CS2 | 17 maps, 316 round wins | -21 s / -9 s | -1.15c / -1.21c (-0.36..+0.43) | price moves first; no profit |
| Dota 2 kills | 9 games, 211 kills | -7 s / -15 s (placebo biased negative) | -1.88c / -2.16c (-0.25..+0.68) | weak timing lead; still negative |
| Dota 2 towers | 63 events, 8 games | -7 s / -11 s | n=14 -1.50c / -2.02c | unknown (too few) |
| Dota 2 barracks | 8 events | n/a | n=0 | unknown |

- TheSports tennis vs Polymarket's own score feed: TheSports is a median 24 s earlier (11 matches, 182 game changes; earlier slim: 15 s). The price moves before both.
- CS2 map points: 2 priced events. Overtime: 0 priced events out of 10. Unknown; the 25 Nov Major is the test.
- Dota 2 kills: 'unknown, weak timing lead'. Placebo half-move is biased negative by the window end (+10 s); net is the cleaner figure and is still below zero.
- Roshan timer starts: 10 (side unknown).
- No new claims of edge. Nothing here supports a taker rule on any of these classes.

## Direction from Nick, 8 Nov 02:28Z (supersedes the verdict wording above)

"So we are far from rejecting TS on tennis or dota. I do not care yet what the losing-money test says because we have not yet begun to sort real signal from noise."

- Tennis and Dota 2: **unknown, signal vs noise not yet separated.** The "no profit" lines in the tables above are a taker test with a 1 s delay, not a test of whether TheSports carries information. They are not a verdict on the feed.
- Work now: per-event lead distributions (not medians) against the random-time placebo, subsets by event type, price level and move size, cluster-bootstrap significance, and the subset known at message time (price not yet moved) where the feed could add something. Script block `SIGNAL=1` in `live/thesports/big_events.py` (run with `POINTS=1 CS2=cs2 DOTA=1 SIGNAL=1`, slims pooled with a colon).

## Signal vs noise, first pass (8 Nov 03:00Z; slim-1102-32295 + final-topics-32295-slim pooled; raw output `reviews/thesports-signal-vs-noise-2026-11-08.txt`)

Method: every event next to the same events shifted by a random 60-600 s (5 each); p values by bootstrap over games (games, not events, are the unit). "QUIET" = price moved <1c in the 30 s before the message, which is known at message time. All figures in cents of the favoured side's mid.

| Class (paired games) | Price already moving before message (t-30..t), real vs placebo | After message (t..t+30), QUIET events, real vs placebo, 90% CI of diff | Lead of price over message (half-move s), real vs placebo | Reading |
|---|---|---|---|---|
| Tennis points (1,194 events, 23 matches) | +1.76c vs +0.02c | +0.37c (n302) vs -0.01c, CI +0.20..+0.58 | -10.2 s vs -8.3 s | **real but small information after the message when the price had not moved**; also the price often reacts first |
| Tennis, underdog-favoured side (fav price 0.10-0.40) | +1.91c vs -0.10c | +0.36c (n79) vs 0.00c, CI +0.21..+0.51 | -9.2 s vs -4.7 s | same, strongest band |
| Tennis, balanced price (0.40-0.60) | | +0.54c (n23) vs -0.06c, CI -0.09..+1.11 | -5.5 s vs -5.5 s | too few quiet events |
| Tennis game-level breaks (58 events) | | too few quiet events | -25.3 s vs -4.6 s, CI -28..-14 | price leads the message by ~25 s on breaks; only 5% of big moves come after the message vs 43% placebo |
| CS2 round wins (452 events, 28 maps) | | -0.03c (n153) vs +0.07c, CI -0.59..+0.35 | -17.4 s vs -7.9 s, CI -14..-5 | price leads; no after-message information |
| Dota 2 kills (237 events, 12 games) | big-move share 38% vs 32% (p=0.04) | +0.43c (n71) vs +0.36c, CI -1.16..+1.25 | -8.8 s vs -11.6 s, CI -4.8..+10.1 | **unknown**: timing indistinguishable from placebo |
| Dota 2 kills, balanced price (0.40-0.60) | | n11, too few | -4.9 s vs -17.2 s, p=0.06 | suggestive (price lags the random-time baseline), not significant |
| Dota 2 towers (62 events) | | | | unknown, too few |

- The one result that survives: tennis, after the message, when the price had not moved. About +0.4c over 30 s on average, significant across the pooled data and in each price band with enough events. 0.4c is below the 1c spread, so it is information but not yet a trade.
- This is about 40 comparisons, so single p values near 0.05 (Dota 2 balanced prices, Dota 2 high-price late share p=0.09) are leads to retest, not findings.
- Caveats: bootstrap over 23 tennis matches, 28 CS2 maps and 12 Dota games; events within a game are not independent; side mapping of CS2 kill-level events is not used here (round wins only).

## Signal vs noise, second pass (8 Nov 03:20Z; three slims pooled incl. `final-topics-32295b-slim` to 02:09Z; raw `reviews/thesports-signal-vs-noise-2026-11-08-pooled3.txt`, tennis state splits in `...08.txt` run on two slims)

- **Tennis, QUIET after message:** +0.33c (n350) vs placebo -0.01c, 90% CI of diff +0.21..+0.48, p<0.01. Same on all 4,095 points seen, 1,419 paired. Stable across states: set 1 +0.46c, set 2 +0.17c, games 1-4 +0.25c, games 5-8 +0.41c, games 9+ +0.29c, first two points of a game +0.53c, 3rd+ point +0.18c, server won +0.41c; returner won +0.19c (CI -0.16..+0.41, not significant). **No state reaches 1c, so no high-leverage subset found yet.** Breaks of serve: price leads by 25 s (51 events, 94% of big moves before -10 s vs 53% placebo).
- **CS2:** price leads (-17.5 s vs -9.1 s, 225 big moves, CI -12..-4); 71% of big moves 10+ s early vs 53% placebo; QUIET after message -0.07c vs +0.10c. No signal.
- **Dota 2 kills (336 events, 15 games):** the earlier balanced-price lead (p=0.06, 12 games) does **not** replicate (-14.9 s vs -9.2 s, p=0.66). New candidate: favourite price 0.60-0.90 and QUIET, after message +1.38c (n30) vs -0.57c, CI +0.80..+3.56 (first pass: +1.50c, n16, p=0.14, same sign and size). Still few games; **unknown, retest on the next slim.** All-price Dota: late share 39.5% vs 33.3% (p=0.26), QUIET after +0.42c vs -0.16c (p=0.17): not significant. Towers: nothing (83 events).
- Pairing is the bottleneck: only 24 of 75 tennis games and 29 of 38 CS2 maps are paired to a PM market by names. `diary/` does not hold names for the newer matches; Hermes asked to refresh it.

## Signal vs noise, third pass (8 Nov 03:50Z; refreshed 8 Nov diary: tennis 30 games paired, CS2 30 maps, Dota 15 games; 30 placebo shifts per event to remove placebo noise; raw `reviews/thesports-signal-vs-noise-2026-11-08-pooled3-diary-npl30.txt`)

No new slim since 02:09Z; this is the same three slims, better name pairing (tennis 23 to 30 games) and a quieter placebo (5 to 30 shifts per event; the 5-shift placebo moved some figures, notably Dota).

- **Tennis, QUIET after message, by favourite price:** all prices +0.39c (n421, CI of diff +0.23..+0.53); fav 0.10-0.40 **+0.62c** (n99, CI +0.27..+1.08); fav 0.40-0.60 **+1.05c** (n30, 20 games, CI +0.48..+2.12, p=0.01); fav 0.60-0.90 -0.14c (n91, CI -0.73..+0.28, none). So the information after the message sits where the favoured side is at most 60%, and is largest at balanced prices; matches the Courtsiding finding that the edge pays in balanced matches. n=30 at balanced prices: needs more matches. Break-point points alone: no signal (n25).
- **Tennis breaks of serve:** price leads the message by 25.6 s vs 10.4 s placebo (65 big moves, CI -20..-9). The feed is behind on breaks.
- **CS2:** price leads by 17.5 s vs 8.4 s (225 big moves, CI -13..-5). QUIET after message: -0.07c vs +0.26c, no signal. Late rounds (loser >=10): -1.96c (n20) vs +0.42c, wrong sign, n20: ignore.
- **Dota 2 kills, fav 0.60-0.90, QUIET:** +1.38c (n30, 15 games) vs +0.04c, CI +0.26..+2.59, p=0.04. Not robust: p was 0.09 with a 5-shift placebo, the 0.40-0.60 band has the opposite sign (-1.50c, n17), and the all-price figure is +0.42c vs +0.04c (p=0.40). Status: **unknown, candidate**. Lead timing indistinguishable from placebo in every band.
- Multiple comparisons: about 60 comparisons in this pass; single p near 0.05 are leads, not findings.

## Signal vs noise, fourth pass (8 Nov 06:15Z; adds Hermes' 06:03Z slim export of final-topics-32295b to ~06:00Z; raw `reviews/thesports-signal-vs-noise-2026-11-08-pooled3-0614Z.txt`)

Data note: Hermes' commit f18045e6 (05:38Z) deleted 22,262 tracked files from the default branch; restored in PR #201 (nothing lost). The 06:03/06:04Z exports were committed without deletions (checked) and look like the first run of the timer.

- **Tennis, QUIET after message, fav 40-60%:** +1.01c (n35, 23 matches) vs placebo -0.10c (30 shifts), 90% CI of diff +0.57..+1.84, p<0.01. Previous pass +1.05c, n30, 20 matches. Stable.
- **Tennis, fav 10-40%:** +0.60c (n100, 31 matches) vs +0.04c, CI +0.29..+0.85. **Fav 60-90%:** -0.13c (n92), none. All prices: +0.39c (n428, 33 matches), CI +0.22..+0.58.
- **Dota 2 kills, fav 60-90%, QUIET:** +1.38c (n30, 15 games) vs -0.05c, CI +0.22..+2.87, p=0.05. No new Dota games in this slim (overnight), so unchanged. All prices: +0.42c vs +0.17c, p=0.57. Still unknown/candidate.
- **CS2:** price leads by 17.5 s vs 8.0 s (225 big moves, CI -13..-6); no signal after the message.

## Tradeability pass (9 Nov 00:30Z; coordinator-authorised; raw: reviews/thesports-tradeability-2026-11-09.txt)
Data: all pooled exports to 22:24Z 8 Nov (tennis 92 matches paired, 89 with big events). Quiet-at-message events only; order lands t+0.2 s +1 s PM sports delay; real vs same rule at shifted placebo times; CI/p bootstrap over games.
- Spread at the event: tennis 10-40% 3.1c (placebo 2.5c); 40-60% 7.3c (placebo 3.6c, widens at messages); 60-90% 3.8c (2.5c); Dota 60-90% 3.1c (2.6c).
- Taker price capture (buy ask, value at mid +60 s): tennis 10-40% -1.32c vs placebo -1.29c; 40-60% -1.49c vs -1.73c; 60-90% -1.65c vs -0.95c (p=0.04, worse); Dota 60-90% -0.06c vs -1.54c (p=0.02, n39, 20 games). Full round trip (sell at bid +60 s): tennis -2.7c to -3.7c, Dota -1.45c vs -3.04c.
  => after the 1.2 s delay the ~1c move is already in the ask; price capture does not beat placebo for tennis. Dota is the only positive (39 events, thin).
- Hold to resolution (taker): tennis 40-60% +12.3c vs +1.4c (p=0.03, 75 events, 23 games); 10-40% -12.2c vs -10.3c (p=0.28); 60-90% +12.3c vs +9.4c (p=0.23); Dota 60-90% +1.8c vs -4.8c (p=0.18). Std per share ~45c, so SE ~5c at n=75: this cannot resolve a 1c edge, and the 40-60% result is one of ~10 tests with no matching price move after entry.
- Bid at best bid (post-only, fill = ask trades down to bid within 60 s): fill 23-36% (placebo 32-43%), queue ahead ~9-13k shares in tennis, ~0.3k in Dota; per-attempt hold EV tennis 10-40% -2.35c vs -4.40c (p=0.09), 40-60% -1.80c vs -0.06c (p=0.55); Dota 60-90% +1.38c vs -3.16c (p=0.14).
Verdict (wording per Nick 8 Nov): UNKNOWN, signal real but tradeability not shown. Settles it: (a) hold-to-resolution needs ~thousands of events (days more data), (b) Dota 60-90% needs more games, (c) entry before the 1 s delay is impossible, so only events where the feed leads the price by >2 s can pay; the lead-time split is the next cut.
