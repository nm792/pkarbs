# URGENT to IT: PandaScore capture retries code 4004 forever (14 Nov 11:50Z)

Fix needed before BLAST Slam (17 Nov). A code change to `live/pandascore/ll_capture.py`, so it is gated; please rule.

## What the recount shows (agent/status/p318-recount-2026-11-14.json, `close_errors`)
- 4,549 of 4,553 close errors are code 4004, ALL on ONE match: **1789154**. That match has ZERO status rows (it is not in `per_match`).
- 4,549 x 10 s = 12.6 h, which is the whole capture window. This is the 10 s sleep in the 4004 branch of `socket_for()`: it does `await asyncio.sleep(10); continue` forever.
- `main()` adds a match to `seen` once and never removes it, so a match that is listed in discovery but unavailable is retried every 10 s until the process restarts.
- Per PandaScore guide section 6, 4004 = match unavailable: re-check discovery for the latest `opens_at`, "do not retry in a tight loop".

## What it is NOT
- Not a breach of the 3-sockets-per-match limit: there are 0 close codes 4029 anywhere. The code opens one socket per match and `async with` closes it before a retry.
- Not shown to cause the gaps over 60 s in the 20 real matches: there are only 4 close errors without a code in total (3 on 1789154, 1 on 1793327). Those gaps are unexplained and may be quiet periods between games. Item 4 of the follow-up note asks you to check.

## Proposed change (3 edits, same file, back up first)
1. `socket_for()`, 4004 branch: replace `await asyncio.sleep(10); continue` with `return` (log `recheck_discovery`). The task ends.
2. `main()`: make `seen` a dict `{match_id: first_start_time}`. A match is started again only if it is in the latest discovery AND at least 300 s have passed since its last task ended. Add a done-callback on the task that records the end time.
3. `socket_for()`: the gate `< open_ts(...) - 5` should be `< open_ts(...)` so we never connect before `endpoint.opens_at` (connecting early also gives 4004).
Also log a `4004_count` per match so a repeat shows up in the next recount.

Cite feeds/STANDARD-feed-latency-test.md for any test impact; this fix changes no test rule. Deadline: applied and a line in agent/status/pandascore.md by 14 Nov 16:00Z, so it is in place long before 17 Nov.
