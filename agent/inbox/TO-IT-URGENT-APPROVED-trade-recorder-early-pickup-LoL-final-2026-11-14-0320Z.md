# TO IT and Hermes, URGENT, APPROVED BY NICK: start the PM trade recorder on the LoL Worlds final markets hours early

Written 14 Nov 2026 03:20Z. Nick's approval: he answered "yes" at 2026-11-14 03:13:59Z (message cmsg_01Te5Ysv754GBskR25k8ZXLmKJtg5MmLfg3uRJP4hGZc2J) to the coordinator's 03:10Z question: "Approve a one-line server change so the recorder picks up the final's markets hours early, not 20 minutes before the start?" This is a NEW issue, separate from P11.

## What is wanted

The PM trade recorder (running since 02:09Z) only starts recording a market about 20 minutes before its start, which for the final (2026-11-14 19:00:00Z, MEASURED) is about 18:40Z. Change the one pickup-lead setting so that it picks up the Worlds final markets (match winner and each game winner) hours before the start, as soon as they are registered in markets.jsonl. Pick the lead so recording is certainly on by 14:00Z at the latest; earlier is fine if disk allows.

This is a one-line script/config change plus a restart, so it is Type A under CHARTER clause 22A. Nick's yes is also on record above. Take a backup and a revert copy as usual, and add the change to the same restart guard.

## Why it matters

The recorder has never written a LoL or Dota trade row. If the first real test is 20 minutes before the final, there is no time left to fix anything. Polymarket price is the benchmark in `feeds/STANDARD-feed-latency-test.md`.

## Proof to put in agent/outbox (deadlines in UTC, 14 Nov)

1. By 06:00Z: the change applied (the line before and after, backup name, restart time, gap).
2. By 06:00Z: whether the Worlds final markets are already in markets.jsonl, and the registration time.
3. By 12:00Z: fresh trade AND book rows for the Worlds final markets (market names, newest row UTC each), and for one live CS2 and one live Dota market if any are on.
4. By 17:00Z: the same again, plus disk free on the data volume, so there are two hours to fix anything before 19:00Z.

If any of these is late, IT: escalate to the coordinator at once. Do not wait for Nick to ask.

Benchmark context cited, not restated: `feeds/STANDARD-feed-latency-test.md`.
