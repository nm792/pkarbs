# SPEC 2026-11-22: NBA paper test, TheSports offline plan, B1 feed-delay plan (R-028, R-029, R-030, R-039)

Status: SPEC ONLY. No NBA recorder, harness or fill simulator exists yet. Every code row below is NOT BUILT until a commit is named, and every row stays UNCHECKED until another thread signs the rule-to-code table (standing rule). Paper only, no orders. All jobs run on Prime under IT caps (R-039); nothing runs in a session container. Each recorder or paper run posts a HEALTH READ within 15 min of start or restart (R-037).

## A. NBA paper test (R-029)

Rule under test (from notes/project-review-2026-11-06.md and Reviewer s.2): after an NBA score event seen on the Polymarket sports WebSocket, post-only bid on the own token the jump model says should rise, at base mid x 0.975 rounded down to 0.001, resting 10 s, held to result. Sim reference: +$9.6/game at 5 s feed delay, 90% range -$0.4 to +$18.9, about $70/day at 7.2 games/day (Reviewer s.2; sim, trade-derived mids, not measured).

Bar (A9): $200/day lower CI. At 7.2 games/day that needs a lower bound of about +$27.8/game, far above the sim's +$9.6. So this test CANNOT clear $200/day stand-alone even if the sim is right: it is judged as a STACK LAYER (stand-alone about 35% of $200 if the sim holds, stack-layer yes, settled by: measured own-token queue and fills, a measured feed delay under 2 s, and 30+ games).

Inputs recorded on ONE host clock (Prime, recv_ns on message receipt):
1. PM sports WS NBA frames (leagueAbbreviation nba). UNVERIFIED that the existing logger keeps NBA rows (the 5 Nov task found none after 3 Nov 06:28Z); the recorder must be proven to write them.
2. Both tokens' own books by websocket for each NBA moneyline, `pm_sport_books.js` with the NBA tag (path on Prime UNVERIFIED: not found on the branches I read; IT to name it). Each book message stored whole with recv_ns.
3. NBA liveData play-by-play with the official timeActual (MEASUREMENT only, never a decision input).

| # | Rule | Code that enforces it | Status |
|---|---|---|---|
| 1 | Decision fires at WS frame receipt only, never at official time | nba_paper/decide.py: input = frame recv_ns; liveData rows are not importable by decide.py (test: import blocked) | NOT BUILT |
| 2 | Base mid from the own token's book at or before recv_ns | decide.py: latest own-book snapshot with recv_ns <= frame recv_ns; none within 5 s = no decision | NOT BUILT |
| 3 | Bid = floor(mid x 0.975, 0.001), size $200 or less, post-only; price, side, size, snapshot id logged at decision | decide.py; decision row written before any later data is read | NOT BUILT |
| 4 | YES and NO books separate; never price NO from YES | decide.py reads only the traded token's book; test: YES-only book gives no NO decision | NOT BUILT |
| 5 | Fill A (trade-through): a later own-token print strictly below our price within 10 s | fillsim.py | NOT BUILT |
| 6 | Fill B (queue): size ahead at our level when we join, reduced only by prints at that level, reaches 0 within 10 s | fillsim.py; both A and B reported side by side | NOT BUILT |
| 7 | Score: 1-minute markout on own best bid plus settlement per game; fee from the market fee field (maker 0, rebate separate) | score.py | NOT BUILT |
| 8 | Event-free placebo: same rule at random times with no score frame | score.py --placebo; real minus placebo reported | NOT BUILT |
| 9 | Plant: inject a raw book/print row set where a known cheap bid fills; recovery must be 95-105% | test_plant.py (rows, not summary figures) | NOT BUILT |
| 10 | Label swap: swap YES/NO labels; edge must vanish | test_labelswap.py | NOT BUILT |
| 11 | Power: games needed n = ((1.645+0.84) x sd / d)^2 with sd = the sim's per-game sd (NOT RE-READ by me; to read from winmodels/us/NOTE-nba-true-event-time-2026-11-04.md data) and d = +$9.6 | power.py | NOT BUILT; sd UNVERIFIED |
| 12 | Stops (pre-set): always-valid 95% interval on per-game P&L; success = lower bound > 0 (reported separately vs the $27.8/game A9 bar); futility = upper bound < 0; max 60 game-days then 'inconclusive, ranked' | stops.py | NOT BUILT |
| 13 | Capacity: shares resting ahead at our price at decision time, per event | fillsim.py capacity column (5 Nov sample median 6,324 ahead) | NOT BUILT |
| 14 | Delay of the feed used = measured (section C), not assumed | B1 result file must exist before any P&L is called valid | NOT BUILT |

Build and run plan (Prime only): recorders first (tonight), harness written and unit-tested against planted rows, first scoring only after one full night of recorder data. No P&L is reported before row 9 and row 10 pass.

## B. TheSports offline (R-028, R-032)

1. Where the data is. Box copy: BOX_ROOT/stale-20261122/vol2/pkarbs/thesports/ holding the final-topics-32295b tree, 10 files, 34,906,107,252 B, transfer_exit=0 06:17:29Z, checksum_exit=0 differing=0 06:21:17Z (agent/status/P101a-stale-ship.md, from /mnt/HC_Volume_107257520/ship/P101a.log). The local VOL2 source was absent by 07:24Z; P101b (the deletion) is NOT verified. Per-file list and sizes: UNVERIFIED, I have no box access, so IT must paste the manifest (the Reviewer-cited reviewer/pkarbs/IT-TheSports-inventory-2026-11-22.md does not exist on branch reviewer). A50 (19 Nov) showed in that tree books.jsonl 23,292,975,394 B, ts_mqtt.jsonl 16,970,673,134 B, trades.jsonl 995,037,907 B. A repo slim copy exists at rn1/scores/thesports/final-topics-32295b-slim (stale: pmws slice ends 12 Nov 05:36Z). CAVEAT: PM market registration failed from 12 Nov 12:39Z (gamma 406, agent/status/thesports-trial.md); whether PM NBA books after 12 Nov exist in books.jsonl is UNVERIFIED (fix approval #21 outcome unknown). Blocker: only IT can read the box.
2. D1 Dota completion offline. Re-pair the 4 registrations of 12 Nov from disk (2,847 tokens through 12 Nov 12:13:43Z, re-pairable per agent/status/thesports-trial.md), then run the pre-registered D1 on the 39 of 40 games with the planted and placebo checks. Rule-to-code table: NOT BUILT; I will copy the pre-registered D1 rule text into it from the 12 Nov registration, not from memory. Runs on Prime from a pinned SHA, from the box copy, read only.
3. TheSports NBA delay. For each of 885 games (6-16 Nov): delay of each TheSports basketball message vs official timeActual, and vs the own-token price (time the own book first moves half of its eventual 60 s move), and the same for the PM sports WS frames in pmws.jsonl, same clock where both exist. Output: median and quartiles of (TheSports minus PM WS) lag; TheSports is worth paying for only if it is faster than the free WS by more than the NBA price lag (about 2.1 s before half-move, 4.9 s median WS delay per the 4 Nov note). Placebo: random event-free times; plant: inject a feed message at a known offset (95-105% recovery). NOT BUILT. No new TheSports access or payment without Nick.

## C. Register B1: NBA feed delay vs the books (R-030)

Question: is any NBA feed under 1 s late vs the own-token book price? Feeds: (a) free PM sports WS; (b) Goalserve NBA live (trial to about 12 Dec; whether it carries NBA play events: UNVERIFIED, I will read its payload docs before any claim); (c) TheSports 6-16 Nov offline only. Method: per event, t_feed = recv_ns on Prime; t_official = liveData timeActual (host NTP offset logged); t_half = first own-book mid crossing half of the 60 s move. Report delay_vs_official and delay_vs_price with medians, quartiles, n, game-clustered CI, placebo times. Pass for B1 = median delay_vs_price under 1 s with CI. Until measured the delay is UNKNOWN and the sim's 0-2 s regime is not supported (the known WS figure is 4.9 s).

## D. 'No fills after 6 Nov' search (R-030 / P-015)

See the result row in INBOX (command and count); search is over every branch's file names and diffs after 6 Nov 03:10Z.
