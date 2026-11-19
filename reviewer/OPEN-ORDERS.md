# OPEN ORDERS: read first (Reviewer, updated 19 Nov 2026 02:02Z)

Every project checks this file and its reviewer branch **at least every 15 minutes while active**. Act on each open order addressed to you within 15 minutes, or name the blocker in a REPLY within 15 minutes. Silence past 60 minutes is a REPEAT. (Standing rule, Nick 02:00Z; also in REPLY-RULES.md.)

| # | project | order | note (repo, commit) | since |
|---|---|---|---|---|
| 1 | MFW | **Kill live clone run 1 now** (INVALID: 802 clone fills vs his 4). Fix the queue model (back of queue, no instant re-join), add a fill-ratio check against his fills, re-run the gate on recorded 18 Nov windows, and go live again only after the Reviewer has checked it. Reply with the kill time. | mfw-clone reviewer/REVIEW-2026-11-19-v3-and-live-rolling.md, a11c9ce7 | 01:50Z |
| 2 | Temperature | **Start the live nowcast** on METAR for 1-2 stations, no orders, p logged on every METAR update for every open bucket, scored continuously, with the 15-minute check committed. No paper trading run and no build until then. | trading-test reviewer/temperature/REVIEW-2026-11-19-nowcast-gate.md, e4bc0f88 | 01:36Z |
| 3 | all | Write all complex code yourselves; the agent only deploys and runs (Nick 01:58Z). | REPLY-RULES.md | 01:58Z |
