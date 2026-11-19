# URGENT to IT: LoL Worlds final, setup check first, then the locked test (deadline 15 Nov 12:00Z)

From: the Goalserve/feeds thread. 15 Nov 2026, 05:20Z. Requested by the coordinator at 05:17Z (Nick's update of 05:17Z). Cites `feeds/STANDARD-feed-latency-test.md` v1; does not restate it. Read-only analysis on Prime's data, Type A, no code or unit change. This file is the pre-registration: it is committed BEFORE any data is read for this test (STANDARD section 4). Prime must not edit it; any change goes in a new dated file.

## Why a setup check comes first (Nick's rule: check the test setup before relaying any verdict)

I have NOT seen that Goalserve carried the final with events. What the repo shows: Goalserve esports payloads are per-poll stat counters plus bet365 odds, no timestamped event stream; the 14 Nov 13:25Z recount lists 24 matches, none named Gen.G or BILIBILI GAMING and none labelled LoL (CS2, Dota 2, one 'other esports'). PandaScore low latency covers CS2 and Dota only. The five Polymarket markets (Match Winner, Games 1-4) were recorded from 11:01Z with books and trades (Prime 19:23Z proof). So 'a LoL feed test against the price' only exists if some feed carried the final's in-game events on the same capture host.

## Step S0, setup check (report by 09:00Z, committed as agent/outbox/lol-final-setup-check-2026-11-15.md)

1. Which feeds captured events for BLG vs Gen.G (final, 19:00Z start, 14 Nov)? For each of: Goalserve esports payloads, TheSports ts_mqtt LoL, any other capture: yes/no, match id, first and last row UTC, row count, and the in-game fields present (kills, towers, dragons, barons, gold, game number). If the match is not in the Goalserve payloads, say so plainly and stop that branch.
2. Same-clock check: feed rows and PM book/trade rows stamped by the same host? State the resolution (poll interval/2, book poll latency).
3. Market mapping: which condition id is Game 1 to 4 Winner and Match Winner; map each feed game number to its market.
4. Event definition per feed (diffed from consecutive messages; STANDARD section 2), and the count of events by type per game. State the total n.
5. Self-consistency: the right match returned (names and start time), no duplicated or out-of-order rows, rows continuous through all games (list gaps over 60 s).

If S0 finds NO feed with in-game events for the final, S1 does not run; the report says 'no testable feed for the final' and why.

## Step S1, locked test (only if S0 passes), report by 12:00Z

Pre-registered rule:
- Feed: each feed that passed S0, tested separately. Benchmark: Polymarket price only (STANDARD section 1). TheSports, if it is the feed, is the tested feed, never the benchmark.
- Events: increases of the in-game counters present, one event per increase: kills, towers, dragons, barons (names as they appear). Game start/end changes are excluded as not price-relevant at 2c.
- Market per event: the winner market of the game in progress; Match Winner is a separate secondary series, reported separately.
- Window, onset, lead, placebo: exactly STANDARD section 2 (onset = first mid move of at least 2c in the event direction within [-60 s, +60 s] of our receive time; 10 random event-free placebo times per match in the same windows, seed 20261115).
- Direction: the event team's win side by settlement of that game, never by price co-movement.
- Bar: STANDARD section 3, items 1-4, unchanged. Match-level clustering: the bootstrap resamples by match. With ONE match (the final) the confidence interval cannot exclude 0 by construction, so the verdict under the Standard is at best 'unknown, settled by at least N further matches' and never a pass. Say that in the report.
- Information only, labelled as such and NOT a verdict: the same bootstrap resampled by game within the final (up to 5 clusters), and the per-event-type split. This is a deviation from STANDARD v1 section 3.3 and needs Nick's approval to count as anything; it is only for sizing how many more matches are needed.
- No money bar (section 5) on one match.
- Numbers labelled 'sim on real data'. No pass or fail wording in the report; give the numbers and the Standard verdict word ('no lead' / 'unknown, settled by ...'). The independent audit (STANDARD section 4) happens before anything is relayed to Nick: do not post a verdict beyond the report.
- One evaluation, no re-picking on the same data.

## Deadlines

- S0 report by 09:00Z, S1 report by 12:00Z (15 Nov). Dispatch had been idle 19:24Z to about 03:20Z and the TheSports team-ID table (PR #346, due 10:00Z) and the Goalserve cricket probe (PD) are also queued: run S0 first, then the team table, then S1, then PD, unless IT rules otherwise and says so in the reply.
- If no session can run S0 by 09:00Z, IT says so in the reply, and the coordinator tells Nick.
- I check the repo at 09:05Z (S0) and 12:05Z (S1) and report each time to the coordinator.
