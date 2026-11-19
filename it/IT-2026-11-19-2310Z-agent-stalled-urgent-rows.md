# IT 19 Nov 2026 23:10Z: urgent rows not yet picked up

1. **Goal:** find and capture live-feed versus Polymarket timing edges in esports and sports (current focus: CS2 PandaScore vs Polymarket books).
2. **Where it stands:** P80, P81 (before 01:00Z), P79 (before 06:00Z), P82 and P0 have been in the queue since 22:40Z (dialogue ee82a6bc; your notes 76781ac, d008b9f). P68a manual run ends about 23:25Z (pkarbs f1254122).
3. **Most important item:** no agent model commit has landed on any project since 21:38Z (dialogue 34965147), so P80 has waited 30 min. IT has written AGENT STALLED at the top of NEEDS-NICK (dialogue eb881a8d) and asked Nick to re-enable the dispatch jobs. If 01:00Z passes without P81, the CS2 daily look cron will miss its first 01:15Z run; plan for that.

No rows changed for PK arbs this run.
