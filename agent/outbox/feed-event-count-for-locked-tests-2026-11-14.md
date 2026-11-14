# Reply to inbox #318 — count qualifying events per locked test (COUNT ONLY)

Posted 14 Nov 04:15Z against the 04:15Z deadline. PARTIAL: the counts that could be measured in the window are below; three items are blocked and named at the end. Script `agent/tasks/p318_event_count.py`, output `agent/status/p318-count-output.json`; full text also appended to `agent/status/pandascore.md` and `agent/status/goalserve.md`.

## Headline

| test | matches captured | qualifying events in a book window | per stratum <$25k / >=$25k | distinct matches |
|---|---|---|---|---|
| PandaScore Dota 2 | 8 (of 20 total) | **0** | 0 / 0 | 0 |
| PandaScore CS2 | 12 (of 20 total) | **0** | 0 / 0 | 0 |
| Goalserve Dota 2 (bet365 odds moves) | 0 in the local window | **0** | 0 / 0 | 0 |
| Goalserve CS2 (round results) | 0 in the local window | **0** | 0 / 0 | 0 |

- PandaScore: 20 distinct `match_id` task_started 13 Nov 15:12:29Z → 14 Nov 04:00Z. `events.jsonl.gz` holds **only lifecycle rows** (`connected` 1,991 / `close_error` 1,967 / `recheck_discovery` 1,964 / `task_started` 26 / `closed` 17 / `start` 2) and **zero** state rows for the whole run; raw hour files hold `status` snapshots only (hour 22: 664 status + 1 hello). `close_error`+`recheck_discovery` ≈ `connected` — a reconnect churn consistent with no state event ever being written. So n = 0: per STANDARD section 3 this is **"unknown, settled by <what, when>"**, and the blocker is the capture, not the sample size.
- Goalserve: the local `esports_payloads/` store holds only hours 14 Nov 02 and 03 (3,659 rows), and **every row parses `events: {}`** — 0 matches, 0 odds updates to diff. Earlier hours were shipped to `<box>` and deleted per clause 2.
- Matches per day (last 24 h): PandaScore **~37/day (estimate)** from 20 matches in 12 h 48 m; date to reach 30 per stratum **not projectable** because events per match is 0. Goalserve per-day **not computable** from a 2-hour local window — no projection offered rather than a guess.
- Goalserve CS2 feed resolution: `agent/tasks/TASK-goalserve-v2-2026-11-12.md` Facts line 13 — `esports/home` **refreshes every 1 minute** (map/round results with win type, no kill events). A 60 s refresh is ~30x the +2 s bar, so **the round-result feed cannot resolve a +2 s lead at all**; 0 round rows observed locally in the 2 hours held.

## Blocked at 04:15Z (per the note's own fallback)

1. Per-match PM book coverage (newest/oldest books row per match): `books.jsonl` is 8.9 GB; the bounded pass over the 1,006 registered cs2/dota2/lol tokens did not complete before the deadline.
2. Volume strata: needs `markets.jsonl` volume joined to those book windows — same blocked pass.
3. Goalserve hours before 14 Nov 02:00Z: on `<box>` only; a box pull is required before any per-day count, and the PandaScore "state events structurally never written vs WS churn" question needs a read of the WS message path, not a count.

No price outcome read, no lead computed, no rule changed — STANDARD section 4 intact.
