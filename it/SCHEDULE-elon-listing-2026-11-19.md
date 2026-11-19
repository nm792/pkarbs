# Elon 48h listing schedule (pipeline thread, 19 Nov 2026 17:25Z)

Evidence: gamma `createdAt` of every `elon-tweets-48h` event since 20 Aug 2026 (40 events): created at 16:07:01Z while New York is on summer time and 17:07:01Z since 2 Nov (EST), every Monday, Thursday and Saturday, gaps 2, 2, 3 days, without a miss. The event for the window opening two days later appears at that second. Dates below are the pattern, not a promise: the recorder detects the real listing by polling every 2 s from 15:55Z to 17:40Z, and the first line of its log states T0 and createdAt.

Standing rule: no missed listing. The first capture (19 Nov) was 5 min 59 s late because the recorder process died; that event is excluded from the primary test.

For each listing (UTC; EST all dates below, 17:07:01Z):
- T-30 min (16:37Z): IT runs `it/elon_listing_preflight.sh` and pastes the whole output. Any FAIL = fix within 15 min or name the exact blocker in the paste.
- T-5 min (17:02Z): IT runs `it/elon_listing_live_read.sh` (pid, 60 s file growth) and pastes it. pid missing = restart the service now.
- T+15 min (17:22Z): thread runs `python3 pipeline/forward/elon_listing.py check --out /mnt/HC_Volume_107257520/elon-listing`; implausible = kill, fix, rerun for the next listing.
- Daily 07:00Z: counts refresh (`refresh_elon_hourly.py`, cron) and one line in the log of its exit code; exit 3 = xtracker blocked: the thread commits `pipeline/forward/data/elon_hourly.json` instead and IT copies it to `/mnt/HC_Volume_107257520/elon-listing/hourly.json`.

| # | listing (UTC) | weekday | window it opens for | T-30 preflight | T-5 live read | T+15 check |
|---|---|---|---|---|---|---|
| L1 | 2026-11-21 17:07:01 | Sat | 23-25 Nov | 16:37 | 17:02 | 17:22 |
| L2 | 2026-11-23 17:07:01 | Mon | 26-28 Nov | 16:37 | 17:02 | 17:22 |
| L3 | 2026-11-26 17:07:01 | Thu (US Thanksgiving; confirm at 16:37) | 28-30 Nov | 16:37 | 17:02 | 17:22 |
| L4 | 2026-11-28 17:07:01 | Sat | 30 Nov-2 Dec | 16:37 | 17:02 | 17:22 |
| L5 | 2026-11-30 17:07:01 | Mon | 3-5 Dec | 16:37 | 17:02 | 17:22 |
| L6 | 2026-12-03 17:07:01 | Thu | 5-7 Dec | 16:37 | 17:02 | 17:22 |
| L7 | 2026-12-05 17:07:01 | Sat | 7-9 Dec | 16:37 | 17:02 | 17:22 |
| L8 | 2026-12-07 17:07:01 | Mon | 10-12 Dec | 16:37 | 17:02 | 17:22 |
The pre-registered pass test needs 15 events with fills: L1 to L8 are about 2.7 weeks; 15 events is about 5 weeks (to roughly 24 Dec). The rule says fewer than 15 = UNKNOWN with the count.
