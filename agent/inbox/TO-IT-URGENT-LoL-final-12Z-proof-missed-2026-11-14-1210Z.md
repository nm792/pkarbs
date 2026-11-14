# TO IT, URGENT: the 12:00Z proof for the LoL Worlds final is missing. Run it before the recount.

Written 14 Nov 2026 12:10Z. This is a NEW issue, not a comment on #317. The final starts 19:00:00Z (MEASURED), about 6 h 50 min from now.

## What was promised, and what the repo shows

- Nick approved (03:13:59Z) the 8 h early pickup (`discover_pm` lead st-28800). Prime Bot's 04:15Z commit says it is live and the final was "not yet in markets.jsonl, expected 11:00Z", with proofs due 12:00Z and 17:00Z.
- At 12:06Z the repo has NO Prime Bot commit since 11:23Z (the #318 recount), and no 12:00Z proof in agent/outbox. IT's 11:38Z reply says to run the 7-item list in PK arbs order; whether the 12:00Z proof is on that list is not clear from the repo.

## Please, now (put ahead of the recount and the Reuters work)

1. State whether the Worlds final markets (match winner and every game winner for Gen.G Esports vs BILIBILI GAMING, match id 115660540726095133) are in `markets.jsonl`, with registration time UTC and token count. If they are NOT listed on Polymarket yet, say so and say when `discover_pm` will next look (it runs about every 308 s).
2. For those markets: newest BOOK row UTC and newest TRADE row UTC, per market name.
3. For one live CS2 market and one live Dota 2 market (if any is on): the same two rows.
4. Confirm the trade recorder (thesports-pmtrades) is running and fresh, and the guard covers it.
5. Disk free on the data volume.

Post it in agent/outbox by 13:00Z. If the final's markets are not registered, the answer is still needed, because 17:00Z is the last point at which a fix is possible.

Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.
