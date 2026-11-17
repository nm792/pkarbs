# URGENT to IT: Goalserve odds inventory, then locked test against the Polymarket price. 17 Nov 2026 06:30Z

Hello IT,

Nick (17 Nov 06:14Z): "check the documents and feed before sending me nonsense" and "if we have not tested them properly then we are wasting the trial." Top priority. Every Goalserve odds claim must come from the stored payloads, not from memory.

What the repo says today, to be checked, not assumed: vendor docs (12 Nov) say live odds are bet365 only, no Pinnacle (agent/tasks/TASK-goalserve-v2-2026-11-12.md). The esports payload top level has a field `bm` that was an empty string in the 13 Nov probe. Nick says Pinnacle odds come from Goalserve. The two cannot both be right, so the payloads decide.

Please send in one reply:

1. **G1, inventory (read-only, no code change). DEADLINE 17 Nov 07:45Z.** From the stored esports payloads (esports_payloads hour files from 13 Nov 15:09Z; sample at least 5 hours spread over 13 to 17 Nov, say which), report in agent/status/goalserve-odds-inventory-2026-11-17.md:
   a. Every distinct bookmaker identifier found: the `bm` value and every bookmaker name or id inside any odds block, with event counts per identifier. State plainly whether "Pinnacle" appears anywhere (yes or no, plus the exact string).
   b. For each identifier: which markets (match winner, map winner, handicap, totals), which titles (CS2, Dota 2, LoL, other).
   c. Update rate per identifier: median and 90th percentile seconds between consecutive changed odds payloads per event.
   d. Which other data fields exist per event (scores, stats, commentary events) with example field names.
   e. For tennis, soccer, baseball and hockey: capture.py stores only hash, size and changed flag (agent/status/goalserve.md), so bodies are NOT available. Say so, and say whether the WebSocket tennis or hockey stream is recorded anywhere (yes or no, path).
2. **G2, locked test. Pre-registration below, locked on commit. Run only after (i) G1 is posted, (ii) the rule-to-code table is signed by a thread other than the one that wrote the code, (iii) the planted-edge check passes. DEADLINE for the run 17 Nov 11:00Z; independent audit before anything is relayed.**

## G2 pre-registration (cites feeds/STANDARD-feed-latency-test.md v1; no deviation)

- **Feed event:** for each bookmaker identifier found in G1 (bet365, and Pinnacle only if G1 finds it), two consecutive stored payloads of the same event whose vig-removed implied probability for the match-winner (or the winner of the map in play) differs by at least 2c. Report each bookmaker separately. Map or match market: use the winner market of the game in progress; Match Winner is a separate series.
- **Market and match:** Polymarket market matched by team names plus start time, side by settlement. Matching rule: exact normalised team names, no fuzzy rule; "X Gaming" versus "X Academy" counts as different teams (known matcher bug in big_events.py `same()`). Print the full match list for audit.
- **Window, onset, placebo, clock, resolution:** STANDARD section 2. Receive time is the capture row recv_ns (one clock). Payload store resolution: one poll of the file, state it. Placebo: 10 random event-free times per match, seed 20261117.
- **Sample:** all matches in the stored payloads from 13 Nov 15:09Z with a matched PM market and book rows. Print n events and n matches per bookmaker and per title.
- **Bar:** STANDARD section 3 (n>=30, median real minus placebo >= +2.0 s, bootstrap 95% CI by match excludes 0, price after the feed in >=60%). Fewer than 30 events: "unknown, settled by <what, when>".
- **Costs:** this is a latency test, there is no money bar unless section 3 passes. If a paper P&L is later computed, fees come only from the Polymarket market feeSchedule rate (rates seen 0.03 to 0.07 on p(1-p); source: the 20 Oct cross-venue pass notes) and observed book depth, with the 1 s sports delay modelled. No cost is invented.
- **Planted-edge check (must pass first):** take real PM series, shift a copy of the feed event times earlier by 5.0 s and confirm the test recovers a median lead of at least +2.0 s and passes the bar; shift by 0 s and confirm it does not pass. Report both numbers.
- **Rule-to-code table:** one row per rule above, with the code line that implements it, signed by a different thread. No table, no run.
- **No verdict is relayed before the independent audit** (STANDARD section 4).

3. **G3, untested data types. DEADLINE for a plan: 17 Nov 08:30Z.** List every Goalserve data type we receive but have never tested against the PM price (per sport: tennis, hockey, soccer, baseball, basketball, volleyball, esports, cricket, rugby). For the ones whose bodies are not stored, give the exact change needed to store them (this is a code change, so Nick approves it; list it as an approval item) and the earliest date we can have n>=30 events.
4. Status line at each deadline even if blocked, with the reason.

Kind regards,
Goalserve/feeds thread
