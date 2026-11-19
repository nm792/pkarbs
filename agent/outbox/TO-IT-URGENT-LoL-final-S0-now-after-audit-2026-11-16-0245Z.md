APPROVALS NEEDED: None. S0 was read-only; no code or live process changed.

RESULT
- Goalserve carried the final in the 14 Nov 18:00–15 Nov 00:00Z window: match 141216907, Bilibili Gaming vs Gen.G, league LOL - World Champs; 9,458 payload rows from 18:45:13.480Z through 23:59:58.895Z. The 13:25Z recount was outside this window and is not used as evidence.
- Payloads provide running counters for kills, towers, dragons and barons. Inferred game boundaries from counter resets / result changes give games 1–4; counter increases were 112 kills, 52 towers, 27 dragons and 10 barons overall. Median poll interval 1.871s (half-interval 0.936s), p90 2.059s, p99 3.974s, maximum 29.580s. Eight poll intervals exceeded 4s; two counter increases (one tower, one dragon) followed those intervals, so their event times are not resolved to <=2s.
- TheSports also captured LoL events for candidate match ID ypq3e3und2vxmd7: 5,031 rows in-window over boxes 1–4, with event-array entries and counter snapshots. The stream exposes team IDs only; the reviewer-requested PR #346 crosswalk covers cricket IDs and cannot map these LoL IDs. This source is not joined to the final by names.
- Goalserve and Polymarket books use receipt/send timestamps from separate processes on the same Prime system clock. The five registered final markets (Match Winner and Games 1–4) map by exact team names and start time (19:00Z); 88,476 book rows for their 10 tokens were present in-window. Measured book request latency (ms−sent): p10 525ms, median 569ms, p90 630ms, max 5,963ms. Contemporaneous NTP offset for 14 Nov is not retained; current chrony reading at 03:34Z was 30.5µs fast.
- S0 establishes a usable named Goalserve feed and game-market mapping, with the stated sparse timing gaps; the note permits S1 because a feed with in-game events exists, but S1 was not run in this session.

DATA
- `/vol2/pkarbs/scratch/lol-s0-20261116/goalserve/` — six verified hourly payload files, 18:00–24:00Z.
- `/vol2/pkarbs/thesports/final-topics-32295b/ts_mqtt.jsonl` and `markets.jsonl`; PM book evidence in `share/books.jsonl.gz`.
- Goalserve per-game counts and event-gap calculations were computed from payloads; no files were changed outside the outbox reply. No duplicate/out-of-order target rows and no target-match gaps over 60s.

OPEN / NOT VERIFIED
- S1 locked test (sim on real data), with Standard v1 onset/placebo rules, remains unrun; deadline 06:30Z. Do not treat the two counter increases following >4s polling gaps as precisely timed.
- TheSports team-name crosswalk for the LoL team IDs is missing; no TheSports market mapping was inferred.

Count: notes run 1 (S0), outstanding 1 (S1), PENDING open 0
