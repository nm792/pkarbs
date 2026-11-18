# CHUNK F (STANDING, daily): run the signed Goalserve odds v2 test once each day, 19 Nov to 8 Dec. Read-only. Posted 18 Nov 2026 02:00Z. Replaces chunk E2.

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve esports odds move before the Polymarket price. Nick, 18 Nov 01:40Z: check it now, the trial is free but limited.

**2. Where we stand.** v2 is signed by the checker (22 of 22 rows, 0a32cf9e). The sequential amendment (daily looks, boundary per look) is in the pre-registration and awaits the checker's re-sign; **do not run F before the sign-off file says SIGNED for the amended commit** (this thread will tell you the commit; the first run is 19 Nov after 00:30Z).

**3. The one item that matters.** Each day, after 00:30 UTC, run the command once on all data since 18 Nov, copy the result file, post the lines below. Same gates as chunk E2 (disk, poll logs for every day since 18 Nov, recorder's own PM files, hour files present, E1 passed). The look number is read from the data; do NOT pass `--seed`, `--plant-c` or any look option.

Use the E2 command (agent/inbox/TO-IT-CHUNK-E2-run-goalserve-odds-v2-2026-11-25-2026-11-17-2250Z.md) with these changes: the day list is 18 up to yesterday (UTC; for 19 Nov only 18; across the month end add the new month's days); output `result-v2-look<K>.json` where K is the number of days since 18 Nov (19 Nov = 1); copy it to `agent/status/goalserve-odds-v2-look<K>-2026-11-<DD>.json`.

**Post daily** (append to agent/status/goalserve.md under `## F look K (date)`): date, `df`, commit and sha256 lines, exit code, then print from the JSON with no interpretation: `look`, `boundary_z`, `data_through_utc`, `plant_c`, `seed`, `files`, `goalserve_events_total`, `drops`, `audit.counters`, `audit.league_prefixes_seen`, `audit.bm_values`, `plain_summary` (all lines), per primary cell `matches_by_day` and `matches_cumulative_by_day`, and `first20_events_biggest_cell`.
**If capture or the poll logs have a gap, say which hours; do not fill them.** The run takes about 5 to 30 minutes of one core, longer as data grows; use `nice`/`ionice` and a 2-hour timeout.
**Done check:** exit 0, `look` equals the number of complete UTC days since 18 Nov, result copied with matching sha256, `plain_summary` printed.
**Stop:** after the look on 8 Dec (K=20) the script refuses; stop then or when this thread says so.
