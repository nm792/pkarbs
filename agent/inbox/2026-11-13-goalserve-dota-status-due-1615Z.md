# To Hermes: Goalserve Dota 2 status, DEADLINE 16:15Z (post at the deadline, finished or not)

Nick asked whether Dota can be checked with another feed. The Goalserve esports capture is that check,
under feeds/STANDARD-feed-latency-test.md v1 (benchmark = Polymarket price, never another feed).
Do not write a second test. Add a section "Dota 2 coverage 16:15Z" to agent/status/goalserve.md with:

1. How many Dota 2 matches inplay-esports.gz has shown since 14:04Z, and how many of them have a
   Polymarket Game-N-Winner market (match by team names; list the matches).
2. The bet365 odds-move events so far on those matches (count, and per match). Use the
   stored payloads from 15:09:35Z plus the hash log for 14:04-15:09Z (changed flag only, no content
   before 15:09Z, say so).
3. Your estimated date to reach 30 priced Dota events and about 10 distinct matches (for the
   match-clustered CI), naming BLAST Slam from 17 Nov. Label it an ESTIMATE, with the rate it rests on.

Wording rule for the verdict: Goalserve has no Dota game events (no kills, towers), only bet365 odds.
Say that. Never call a result an edge until it passes the locked test.

Also add (still owed): a stored esports payload parses and shows team names, and round/kill fields where present.
Cite the standard, do not restate it. No credentials in the repo.
