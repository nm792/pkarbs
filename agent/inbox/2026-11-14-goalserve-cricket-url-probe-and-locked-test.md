# TASK for Hermes: find the Goalserve cricket live URL and check it from the whitelisted IP (due 14 Nov 07:00Z)

Written 14 Nov 2026 04:40Z. Nick asked for Goalserve cricket for the BBL (starts 12 Dec) and to see whether the URL can be found. Status line in `agent/status/goalserve.md` by the deadline, UTC, with MEASURED labels. No credentials in any file.

## What is already known (repo and public pages)

- Goalserve's public cricket page lists live scorecards, ball-by-ball commentary, odds and player profiles, and says the cricket live score feed updates every 5 seconds (another page says ball-by-ball within one second). That is marketing copy, so it is UNVERIFIED until measured.
- The same page says feed samples and structure come from support@goalserve.com. No public docs URL for the cricket endpoints was found.
- `inplay-cricket.gz` returned 404 on 13 Nov (measured; there is no in-play file for cricket). The `cricket/livescore` path returned 400 on livescore.host and 404 on the inplay and live hosts (status file, 13:25Z). So the cricket live feed is not in the in-play file set.
- Existing esports/tennis files use the in-play host with `?user&key`; the WebSocket token (POST gettoken with `{"apiKey": KEY}`) works and `wss://live.goalserve.com/ws/<sport>?tkn=<token>` answered for tennis and esports.

## Please measure, in this order, from the whitelisted IP (157.180.24.89)

1. Try the WebSocket channel for cricket: `wss://live.goalserve.com/ws/cricket?tkn=<token>` (and `/ws/cricket-live` if that name is rejected). Record: connected yes/no, close code, first 5 messages' keys (no values that contain credentials), message rate over 60 s.
2. Try the standard Goalserve cricket REST pattern for live scores under the feed host used for the other sports: `/getfeed/<KEY>/cricket/livescore?json=1` and `/getfeed/<KEY>/cricket/home?json=1`, on the feed host that already works for tennis (do not guess hosts that return DNS errors). Record HTTP code, bytes, and whether any match is live now.
3. Look in the account's feed index or documentation page under our login for the cricket section name, if the account area exposes one. Record the exact path you used. Do not paste the key or login.
4. If none of 1 to 3 works, say so in one line and list what to ask support@goalserve.com for (exact endpoint name for live ball-by-ball, update rate, and whether it is in the current plan). Do not email; Nick sends external email.
5. If any live cricket match is on now (any league), capture 10 minutes of the feed to the data disk (not root) and report: rows per second, whether ball events carry a timestamp, event types seen (ball, wicket, boundary, over end), and the fields that identify the match and ball number.

Cricket is the only task; do not start any other capture to do this. Disk floor 15 GB applies.

## Draft locked test (do not run it yet; it needs live matches and PM books)

Standard: `feeds/STANDARD-feed-latency-test.md`. The benchmark is the Polymarket price, never another feed. Cite it, do not restate it.

- Unit: one cricket event = a wicket, a boundary (4 or 6), or an over end, identified by match id and ball number in the Goalserve cricket feed, first-seen time = recv_ns of the first poll or message that shows it.
- Market: the Polymarket match-winner (and, where listed, innings-runs) market for the same fixture; book rows from the same server clock (books.jsonl, 1 s) so both sides use one clock.
- Window: price change from first-seen minus 30 s to first-seen plus 60 s; placebo = same-size windows at random times inside the same match.
- Pass bar, as in the Standard: at least 30 events, lead at least +2 s over the random-time placebo, confidence interval excluding 0, price moves after the feed in at least 60% of events. Fail on any one.
- Lock before looking: the event list, the window, the placebo draw (seeded), and the bar are written to the repo with a commit time before any price is joined.
- Capture first: until the live URL exists and a match is on, nothing can be counted. The count step (events with both a feed row and a PM book row) is allowed once data exists, count only.

## What earlier cricket tests showed, so nobody repeats them

- TheSports cricket 48 h trial (10 Nov 04:05Z to 12 Nov 04:05:18Z, bounded by `timeout 172800`): 62,009 ts_mqtt rows, 14.8 MB pmws. The status files show no verdict from it; no locked test was run on it.
- The 10 Nov repo memory line "Cricket: ESPN ties PM" is an ESPN result, not a TheSports verdict.
- The 3 Nov cricket NPL ball-by-ball windows (250 and 197 rows) were collected from a v2 API, count only; no verdict.

Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.
