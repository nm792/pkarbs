# URGENT: the #318 "0 qualifying events" is a counting error, recount from the raw rows (14 Nov 2026, due 05:00Z)

Standard: feeds/STANDARD-feed-latency-test.md v1. Task: agent/tasks/TASK-pandascore-trial-2026-11-12.md Part B (events are DIFFED from consecutive status messages).

## What the 04:15Z reply got wrong (from the repo, agent/status/pandascore.md and goalserve.md)
1. PandaScore: `events.jsonl.gz` is lifecycle-only by design (`ev(kind=...)` writes connected, closed, recheck and so on). State events are not written there. They are derived by diffing the `status` rows in the raw hour files. Hermes did exactly that at 16:10Z (157 kill-side, 43 tower, 21 barracks, 19 roshan changes across 3 Dota matches, inbox #305). The same raw files still hold those rows, so "0 state events ever written" and "never at this event rate" are not findings. The raw hour files show 664 `status` rows in hour 22 alone.
2. Goalserve: the local payload store holds only the last hours (14 Nov 02-03Z, no live esports), and the earlier hours were shipped and deleted. `events:{}` on those rows is expected. The count must read the earlier hours from the box copy.
3. A real question remains: `close_error` 1,967 and `recheck_discovery` 1,964 against `connected` 1,991 over about 13 h. That is a reconnect loop of about 2.5 per minute. It may be harmless (sockets for matches that have not opened, code 4004) or it may drop messages mid-match. The status file does not say which close codes.

## Do now, count and read only, no code change, no rule change
A. PandaScore: re-run the 16:10Z diff method on ALL raw hour files since 13 Nov 15:12Z (local plus box, tolerant gzip reader, hour 22 BADGZ included). Report, per title (Dota 2, CS2) and per match: kills, towers, barracks, roshans (Dota), round-score changes and `alive` flips if `player_alive` is in `available_fields` (CS2). Give totals and distinct matches.
B. Close codes: for the `close_error` rows, give the count by close code (or none), by match, and say whether any match with live status rows shows a gap in `recv_ns` longer than 60 s. Say plainly whether the churn costs data.
C. Goalserve: re-run the odds-move count (any `value_eu` or `suspend` change between consecutive stored payloads) on the box copies from 15:09Z 13 Nov onward, by match, Dota 2 and CS2 separately.
D. Then, by 06:00Z: per-match PM books coverage and volume strata (< $25k and >= $25k) as named in #318, using only the registered tokens and only windows from 13 Nov 17:06Z, so the 8.9 GB `books.jsonl` pass is bounded.

Write A to C into agent/status/pandascore.md and agent/status/goalserve.md by 05:00Z, and D by 06:00Z. Name the script and output path. If something blocks, post what at the deadline.
