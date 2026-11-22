# REVIEW 2026-11-22 05:45Z: was TheSports wrongly discarded? and an NBA paper test

Asked by Nick 22 Nov 05:22Z ("did we wrongly discard TheSports? NBA is fine to test"). Read-only. Judged against reviewer/MODELLING-PRINCIPLES.md (dead = evidence of no edge, not a failed significance bar).

## 1. Verdict on TheSports: partly. Tennis and esports kills are dead with evidence; NBA, Dota-objective, LoL and cricket were dropped untested

The stop on 20 Nov (Nick 03:16Z "no use"; PK P72 c849817814 "no current Goalserve test needs it") was a disk decision. It cited no edge evidence. The evidence that does exist, sport by sport:

| TheSports sport | Evidence | Does it show no edge? | Classification |
|---|---|---|---|
| Tennis, decisive points (break/set/tiebreak/any decisive) | Lead-share test 9 Nov (`reviews/thesports-lead-share-2026-11-09-0725Z.txt`, e8ad2ac37e; match-clustered, placebo at event-free times): share of the [-60,+60] s favourable move already in the price when the message arrives = 0.86 [0.83,0.89] any decisive point (93 matches), 0.97 break converted (85), 0.99 set point (54), vs placebo 0.43-0.48 | YES for a taker: the price has done ~90% of the move before the message. The PM book clock in that test was the REST poller, whose staleness can only make the price look LATER, so the result is conservative | DEAD for taker-on-message (measured) |
| Tennis, rule T1 (point, quiet price, mid 0.40-0.60, taker at ask +1.2 s, hold to resolution) | `reviews/thesports-T1-result-2026-11-12.md`: 60 matches, real minus placebo -3.43c, 90% CI [-9.96, +3.35] | Partly. It rules out a T1 edge above about +3.4c/share. Power was 80% only for +10c (per-match sd 28.7c, held to resolution); for +2c it was about 14%, for +3c about 20% (my calculation: z = d / (28.7/sqrt(60)) vs 1.645). The prices were the token's own ask (big_events.py:1097), not mirrored | DEAD above +3.4c; 0 to +3.4c gross NOT TESTED (and must clear the 1.25c taker fee) |
| CS2 kills / headshots | Same lead-share file: 0.45 [0.41,0.49] vs placebo 0.47; mtm60 real-minus-placebo +0.14c [-0.47,+0.82] (25 matches); held -0.93c [-1.63,-0.22] | YES: indistinguishable from random times, CIs within about +-1c | DEAD (measured, small sample) |
| Dota kills | 0.43 [0.38,0.48] vs 0.46 (18 matches) | YES at that sample | DEAD (measured, 18 matches) |
| Dota objectives (Roshan, barracks, first blood) and rule D1 | Roshan 8 events, first blood 12, barracks too few; D1 had 39 of 40 games and was never evaluated (PM market discovery broke 12 Nov 12:39Z: gamma `/events` limit>50 needs `Accept-Encoding: gzip`) | NO evidence | UNTESTED |
| NBA | 885 games, 1.77M basketball messages captured 6-16 Nov (inventory in the same file); never analysed. NBA was dropped by Nick on 7 Nov, which Nick has now reversed | NO evidence | UNTESTED |
| LoL | 6 matches, "too few" in every class | NO evidence | UNTESTED |
| Cricket | 48 h capture 10-12 Nov, 62,009 messages; count/locked-test draft only (inbox #324) | NO evidence | UNTESTED |

Access: the free trial ended 16 Nov and was not paid (rule at the time: "No paying or extending"). So new live TheSports tests need a paid or new trial, which is Nick's decision. The recorded 6-16 Nov data (TheSports messages plus the PM book poller in `thesports/final-topics-32295*`, partly in the repo as `rn1/scores/thesports/final-topics-32295*-slim`) can still be tested offline if it was not deleted. IT asked on 20 Nov 09:25Z whether to delete final-topics-32295b (65b6db323a); no answer is on any branch, and T0k3 ships files older than 7 days to the storage box.

## 2. NBA paper test (R-029)

What exists: the free Polymarket sports WS reaches us a median 4.9 s after the NBA official play, 2.1 s before the price is half-moved, with 33% of the move done (n 1,209 scores, 14 games, `winmodels/us/NOTE-nba-true-event-time-2026-11-04.md`). The simulated rule (post-only bid at mid x 0.975 rounded down to 0.001, side the jump model says should rise, 10 s, held to result, fills only on prints trading strictly through our price) gives about +$9.6/game at 5 s, 90% range -$0.4 to +$18.9, about $70/day at 7.2 games/day. It is a sim on trade-derived mids, 429 games of 2025-26; the 2026 sample held to result was -$42/game at 0 s on 39 games. No paper or live order was ever placed (the NBA book recorder task was cancelled 7 Nov).

Minimum valid paper test (MODELLING-PRINCIPLES 8, 10, 12, 13, 14):
1. Recorders, one host clock: Polymarket sports WS NBA frames (recv on message) and both NBA tokens' own books by websocket (`pm_sport_books.js` with the NBA tag; it was built for NHL+NBA on 20 Nov and cut to NHL). Plus NBA liveData play-by-play for the true event time (measurement only, never a decision input).
2. Decision on information at WS receipt only: base mid from the own book at or before receipt; the bid price, side and size logged at decision time with the book snapshot id.
3. Fill rule on the own token only: a later print strictly below our price, or our queue position (own-book size ahead at our level when we join, reduced only by prints at that level) reaching zero within 10 s. Both reported; no mirrored side.
4. Score: 1-minute markout and settlement, per game; costs at the market's fee field (maker 0; rebate kept separate).
5. Controls before any number: event-free-time placebo, plant injected as raw book/print rows (recovery 95-105%), label swap; power from the sim's per-game sd; pre-set success and futility stops.
6. Capacity: shares resting ahead at our price at decision time (the 5 Nov sample had a median 6,324 ahead), reported per event.

## 3. Offline TheSports checks that cost no new access (R-028)
- D1 Dota: finish with the 12 Nov registrations re-paired from disk (PK's own 13 Nov status said they were re-pairable), evaluated exactly as pre-registered, with the planted and placebo checks.
- NBA: the 6-16 Nov TheSports basketball messages vs the PM sports WS (`pmws.jsonl`) and the PM NBA books in the same folder: delay of each against the official `timeActual` and against the price. That tells whether TheSports NBA is faster than the free PM stream, which is the only reason to pay for it.

Confidence 7/10. Below 9 because: the lead-share and T1 results are the project's own runs (I checked the method and the pricing code, not every number); whether the 6-16 Nov raw data still exists is unknown; the NBA sim is on trade-derived mids. To reach 9: PK confirms where the 6-16 Nov folders are, and an independent rerun of the lead-share file.
