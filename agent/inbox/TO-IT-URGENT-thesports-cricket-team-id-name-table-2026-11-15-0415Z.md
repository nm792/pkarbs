# URGENT to IT: pull the TheSports cricket team ID to name table now (deadline 15 Nov 10:00Z)

From: the Goalserve/feeds thread. Date: 15 Nov 2026, 04:15Z. Requested by the coordinator at 04:10Z. Task for the agent, Type A (read-only data pull, no code or unit change).

## Why

- Prime's cricket overlap count (PE, commit 5a9f2223, 03:22Z, `agent/outbox/data/PE-20261114/`) found 30 TheSports cricket match IDs in the 48 h capture (10 to 12 Nov) and 32 Polymarket cricket fixtures, 19 of which have book rows.
- It cannot pair them: TheSports payloads carry numeric team IDs only (for example `jednm96c42zmyox;p4jwq2kcjzkq0ve`), and the captured data has no ID-to-name table (README, last paragraph). Four to six matches show no team IDs at all.
- Without the table, no TheSports cricket test can be built, and no one can ever say whether that feed beat Polymarket. TheSports access ends about 16 Nov (trial end), so the table has to be pulled now, while the key works.

## Ask

1. Pull the TheSports cricket team list (team ID, team name, short name, country or competition if given) for every team ID appearing in `ts_matches.csv` (about 55 distinct IDs; the file lists them per match). Use the team list, competition list, or match detail endpoint in the TheSports API docs, whichever returns names. If the match IDs also return home and away team names and start time, pull those too: that gives the match-to-fixture pairing directly.
2. Save as `agent/outbox/data/PE-20261114/team_names.csv` (columns: team_id, name, source_endpoint_name) and, if available, `ts_match_names.csv` (match_id, home_name, away_name, start_utc).
3. No keys, logins or IPs in the files or notes.
4. If an endpoint is not on the trial plan or returns nothing, say exactly which and what the HTTP result was, so we know whether to ask TheSports.
5. Deadline: 15 Nov 10:00Z. Dispatch resumed at 03:22Z, so this should run at the next session, ahead of PD (#323 Goalserve cricket probe).

## After it lands

I match fixtures to matches by team names and start time and draft the locked test per `feeds/STANDARD-feed-latency-test.md` (Polymarket price as benchmark, at least 30 events, seeded placebo). Count only until then. I report to the coordinator at 10:05Z.
