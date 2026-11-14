# Count qualifying events per locked test, 14 Nov 2026 (COUNT ONLY, due 04:15Z)

Standard: feeds/STANDARD-feed-latency-test.md v1 (cited, not restated). Nick asked when each locked test reaches n >= 30 events. Nothing in the repo counts them yet. This is a read-only count. It reads no price outcome, computes no lead and changes no rule, so it is not a peek under STANDARD section 4.

For each of PandaScore Dota 2, PandaScore CS2, Goalserve Dota 2 (bet365 odds moves) and Goalserve CS2 (round results), report from the captures to 14 Nov 04:00Z:

1. Matches captured, and how many of them have PM books recorded in `books.jsonl` (newest and oldest books row per match). Registration was dead 12 Nov 12:39Z to 13 Nov 17:06Z, so matches in that window may have no books.
2. Events (per the task's event types) that fall inside a recorded book window, in total and per volume stratum (PM match volume < $25k and >= $25k). Also give the number of distinct matches behind them.
3. Matches per day captured over the last 24 h, so the date to reach 30 per stratum can be projected. Label the projection "estimate".
4. For Goalserve CS2, say the resolution of the round-result feed (the docs say the score feed refreshes about once a minute), because that decides whether a +2 s lead can be measured at all.

Write the answer to agent/status/pandascore.md and agent/status/goalserve.md. Name the script and the output path. Deadline 04:15Z. If you cannot finish, post what is blocked at 04:15Z.
