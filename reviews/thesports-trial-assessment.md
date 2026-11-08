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
