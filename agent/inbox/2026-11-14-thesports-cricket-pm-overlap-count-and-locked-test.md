# TASK for Hermes: does the TheSports cricket capture (10-12 Nov) overlap Polymarket price rows? COUNT ONLY, due 14 Nov 06:30Z

Written 14 Nov 2026 04:55Z (coordinator request, for Nick's question about TheSports cricket). Post the result in `agent/status/thesports-trial.md` with MEASURED labels. Count only: no price joins, no lead numbers, no verdict.

## What the repo shows (read 04:50Z)

- The cricket capture ran 10 Nov 04:05Z to 12 Nov 04:05:18Z with `--no-books`, so it recorded NO Polymarket order books itself. It did record `pmws` (the Polymarket sports WebSocket, 14.8 MB; this is a score/status feed, not an order book) and 62,009 `ts_mqtt` rows on `thesports/cricket/match/v1`.
- The repo slim export `rn1/scores/thesports/final-topics-cricket-slim/counts.json` lists only 8 hourly buckets (10 Nov 04:00Z to 12:00Z, 8,561 rows in total), not 62,009. The 62,009 figure is from the status file; the slim file may be a subset. Please say which is right.
- The other recorder, capture-b (`final-topics-32295b`, books at 1 s for registered markets), was running through this period. Whether it held cricket markets is UNKNOWN to me.

## Count these (from the box, data disk, no root files)

1. Cricket markets in `markets.jsonl` (capture-b) registered between 10 Nov 04:00Z and 12 Nov 12:34Z: count, and list market names and the matches (teams, league) they belong to.
2. For those markets, rows in `books.jsonl` between 10 Nov 04:05Z and 12 Nov 04:05Z: rows per market, first and last row UTC.
3. TheSports cricket matches with ts_mqtt rows in the same window: match ids, teams, first and last row UTC, rows per match (check the 62,009 vs 8,561 question here).
4. Overlap: matches that have BOTH ts_mqtt rows and PM book rows for the same fixture (pair by team names), and for each the count of candidate events (wicket, boundary, over end) visible in ts_mqtt. Say how events are identified in the payload (field names), or that they are not identifiable.
5. If the overlap is under 30 events, say so in one line; the Standard needs at least 30.

## Draft locked test (do not run until the counts are posted)

Standard: `feeds/STANDARD-feed-latency-test.md`. Cite, do not restate. Benchmark is the Polymarket price, not another feed. Unit, window, placebo, pass bar and lock rule: as in `agent/inbox/2026-11-14-goalserve-cricket-url-probe-and-locked-test.md`, with TheSports `ts_mqtt` first-seen time as the feed side. Both sides use the server clock. Events, window and seeded placebo draw are committed before any price is joined. Only a test that runs on the locked list counts; a count of 30 or more is needed before it is worth running.

Note on a claim to correct: the repo has no TheSports cricket verdict. The 10 Nov repo line "Cricket: ESPN ties PM" refers to an ESPN feed, not TheSports.

Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.
