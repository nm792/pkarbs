# TASK (REPOINTED 18 Nov 18:20Z): BLAST Slam IX Dota, 20 Nov onward. Measure the feeds we have on trial, NOT Valve (OPEN)

Owner thread: "Find a fast live Dota 2 feed". Nick, 18 Nov 18:14Z: "we are not testing Valve". **All Valve-feed work is stopped.** Do NOT start `capture.js` (it polls Valve and records only the first token of each market). The 16-17 Nov Valve analysis is finished (out_lag_2026-11-16.*, 50261e5808): no league under 60 s; nothing more to run.

Goal: lead of each Dota feed we already pay or trial for versus the Polymarket price, per STANDARD v1 (feeds/STANDARD-feed-latency-test.md), on BLAST Slam IX games (20-29 Nov; first six group games 20 Nov 11:00, 14:00, 17:00Z). Benchmark = each Polymarket token's OWN book (YES and NO separately; never NO = 1 - YES) plus trades.

Feeds under test (no new feed, no new capture process unless a gap is found):
1. PandaScore Low Latency WS (Dota 2), trial to 1 Dec: existing `live/pandascore/ll_capture.py`.
2. Goalserve esports (inplay-esports.gz, bet365 odds, plus esports/home score): existing esports capture.
3. Polymarket benchmark: existing trade recorder and book recorder.

## IT: verify and report by 20 Nov 09:30Z (before the first game), then by 13:00Z after the 11:00Z game
Reply in it/ on branch reviewer. Read-only checks; change nothing without a task row.
1. PandaScore: is `ll_capture.py` running (PID, start time; pre-339 patch state per agent/status/pandascore.md)? Does `low_latency_feeds` list the BLAST Dota matches, and does the capture open a socket per match? After the 11:00Z game: file names, sizes, message counts per match id, reconnects/close codes.
2. Goalserve esports capture: running? Last file time, sizes; does inplay-esports contain the BLAST Dota games after 11:00Z (count of rows naming the teams)?
3. Polymarket benchmark: do the recorders store the book and trades of BOTH tokens (YES and NO) for each BLAST Dota market (Game 1/2/3 Winner, match winner)? List which condition IDs / token IDs are covered, from config.json in agent/tasks/dota-live-capture-2026-11-20/ (8 series, 20 Nov; tokens[0] = first outcome, tokens[1] = second). **If any BLAST token is not recorded on its own book, say so by 09:30Z with the list; do not improvise.** We then add a small PM-only recorder row.
4. Data volume: `df -h /mnt/HC_Volume_107257520` showed ~10.9 GB free at 18 Nov 02:12Z (below the 15 GB floor / 20 GB gate, agent/status/goalserve.md). Report free space now and the projected use by 29 Nov (Goalserve ~279 MB/day esports plus ~2.8 GB/day store-all, PandaScore, books). If the projection breaches the floor, say which store to trim or move; do not delete data without Nick's word.
5. All outputs stay on /mnt/HC_Volume_107257520. Never rely on a storage-box copy as the only copy.

## Analysis (after each BLAST day)
Per game: feed event time (our receive time) vs the first move of that token's own book/price >= 2c, with placebo, n per STANDARD v1; PandaScore events = kills, towers, barracks, roshan diffs per game_id; Goalserve = bet365 winner price move >= 2c. Small result files only in git. Rule-to-code table and checker per the Reviewer rules before relaying any pass/fail.

## Retired
Valve capture (this file's previous Part B, PR #415 version) and the 16-17 Nov Part A.
