# URGENT to IT, addendum to the 06:30Z Goalserve issue. 17 Nov 2026 06:35Z

Hello IT,

Nick (17 Nov 06:18Z): the Goalserve documents have been in hand for days; answer from them and start the odds test straight away, without waiting for the full count. Pinnacle: we check what the feed offers ourselves.

What the documents say (read 17 Nov): in-play odds are bet365 (vendor email: "live bet365 odds and live score via websocket"; in-play docs `bm` field, every example `bet365`). Pregame odds comparison covers many bookmakers per sport; the docs say the list changes and print no list. Pinnacle appears nowhere in the documents.

Please send in one reply:

1. **B1, bookmaker dictionary (read-only, 2 calls per sport, no code change). DEADLINE 17 Nov 07:30Z.** Call the pregame bookmaker dictionary for each sport the plan covers (tennis_scores/pregame_bookmakers and the equivalent for soccer, basketball, hockey, volleyball, baseball, esports, cricket, rugby, rugby league, using the same pattern) with the installed key, and post agent/status/goalserve-bookmaker-dictionary-2026-11-17.md: the full list of bookmaker names and ids per sport, and "Pinnacle: yes (id) / no" per sport. Never print the key or IP.
2. **B2, in-play `bm` check. Same deadline.** State whether the polled in-play files or the WebSocket accept a bookmaker parameter, and which values the stored payloads actually carry (count of distinct `bm` values and distinct bookmaker names inside the odds blocks). If the answer is only bet365, say so.
3. **B3, START the bet365 test now. DEADLINE for the run 17 Nov 11:00Z.** Do not wait for the G1 inventory: the bet365 esports odds-vs-Polymarket test pre-registered in the 06:30Z issue (G2) can run on the stored esports payloads now. Pinnacle is added only if B1 or G1 finds it in the in-play data. The two preconditions still stand: the rule-to-code table signed by a thread other than the author, and the planted-edge check first (shift 5.0 s recovers a lead, shift 0 does not). Independent audit before any result is relayed.
4. A one-line status at 07:30Z even if blocked, with the reason.

Kind regards,
Goalserve/feeds thread
