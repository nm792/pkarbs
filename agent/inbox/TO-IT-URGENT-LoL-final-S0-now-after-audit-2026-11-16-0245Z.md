# URGENT to IT: run the LoL final setup check (S0) right after the PandaScore audit, report by 16 Nov 04:00Z

From: the results thread, 16 Nov 2026, 02:45Z, on the coordinator's instruction after Nick asked "what about LoL?". The pre-registration is unchanged: `agent/inbox/TO-IT-URGENT-LoL-final-locked-test-setup-check-first-2026-11-15-0520Z.md` (S0 then S1). This note only changes the ORDER and DEADLINES and adds three S0 questions. Order: PS audit (OPEN PA), then LoL S0, then S1 if S0 passes. S0 report by 04:00Z (was 15 Nov 09:00Z, then 13:30Z, never run). S1 by 06:30Z. Cites `feeds/STANDARD-feed-latency-test.md` v1.

## Three additions to S0 (answer in the S0 report)
1. **The 14 Nov 13:25Z recount does not cover the final.** It ended 6 h before the 19:00Z start, so 'none of the 24 recount matches is LoL' says nothing about the final. Check the Goalserve esports payload files from 14 Nov 18:00Z to 15 Nov 00:00Z for the final (Gen.G Esports vs BILIBILI GAMING, or any LoL match) and say yes or no with row counts.
2. **If Goalserve carries it only as running counters** (per-poll totals, no event time): give the poll interval, and so the time resolution (poll interval / 2). STANDARD section 3 needs a lead of at least +2.0 s; if the resolution is worse than that, say 'cannot be timed to the Standard by this feed', with the evidence and n (count of counter increases per game), and stop that branch.
3. **TheSports ts_mqtt LoL** (the stream was live from 11:01Z): does it hold in-game events for the final (kills, towers, dragons, barons), with team names or only ids? If only ids, use the table from PR #346 if it exists, or say the crosswalk is missing.

If NO feed can time in-game events for the final, S1 does not run; the report says 'no testable feed for the final' with the evidence above. Do not edit the earlier note. No pass or fail wording beyond the Standard's verdict words.
