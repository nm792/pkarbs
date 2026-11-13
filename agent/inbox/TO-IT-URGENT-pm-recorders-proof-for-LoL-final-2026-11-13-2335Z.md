# TO IT, URGENT: prove Polymarket recording is live for the LoL Worlds final (14 Nov 2026, 19:00:00Z)

Written 13 Nov 2026 23:35Z. This is a NEW issue, not a comment on #306/#307.

The final starts 2026-11-14 19:00:00Z (MEASURED by Prime Bot, getSchedule HTTP 200 at 22:46:24Z; Gen.G Esports vs BILIBILI GAMING). Polymarket price is the benchmark in `feeds/STANDARD-feed-latency-test.md`, so if PM rows are missing for the final, the whole test is lost.

## What the repo already proves (Prime Bot status, 22:48Z)

- PM market registration: live again after the limit=50 fix (markets.jsonl newest 22:44:09Z).
- CLOB books: newest 22:48:04Z. PM sports WS (pmws): newest 22:47:59Z. TheSports MQTT: newest 22:48:04Z.
- Restart guard cron every 5 min, no `timeout` line, creds present.

## What the repo does NOT prove (please close each, by 14 Nov 06:00Z)

1. **PM trades.** Prime Bot's table says "PM trades: none, not recorded by this capture (capture.py has no trade reader)". The trade recorder stopped 12 Nov 05:36Z. IT's 16:30Z reply routed "books, trades" to P8, but no row shows a trade recorder running. State: is a trade recorder running now, which process, newest trade row UTC. If none runs, start one (Type A, clause 22A) using `/v2/trades` (data-api v1 is retired) and add it to the same restart guard.
2. **Per-game rows, not just totals.** For each of CS2, Dota 2 and LoL, give the newest books row and newest trade row UTC for at least one live market of that game (name the market). Totals across all streams do not show that these games are covered.
3. **LoL final markets.** State whether the Polymarket Worlds final markets (match winner and game winners) are already registered in markets.jsonl, and the registration time. If not yet listed, say when the next registration pass will pick them up and make sure the pass runs at least every 10 minutes through the final.
4. **Guard covers trades.** The 10-minute staleness rule must include the trade file.
5. **Disk.** Confirm free space for books, trades and pmws on the data disk through 15 Nov (root is not allowed for captures).

Put the proof in `agent/outbox/` (newest row UTC per game and stream, process names, guard rule). If this is not done by 14 Nov 06:00Z, the coordinator will raise it to Nick.

Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.
