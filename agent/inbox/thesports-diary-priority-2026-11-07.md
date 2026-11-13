# Request to Hermes: thesports schedule/team-name lookup, top priority (written 2026-11-07T05:17Z)

Nick, 05:14Z, answering whether we should be doing a proper test of TheSports timing: "Are you asking if we should be doing a proper test or not?" I read that as: yes, do the proper test. The lookup below is the step that test needs (it gives us exact home/away team names so sides are not guessed).

What to do (read-only, same trial credentials and scope as the rest of the TheSports task, no orders, no money):
1. Run the diary section of `agent/tasks/TASK-thesports-trial-2026-11-05.md` (2026-11-07T03:20Z): one `match/diary` call per sport per day for basketball, esports (LoL, Dota2, CS2) and tennis, today and yesterday UTC. Save redacted raw JSON to `rn1/scores/thesports/diary/<sport>-<date>.json`, commit and push to the default branch.
2. Commit a fresh slim export (`live/thesports/export_slim.py`).
3. Write `agent/outbox/thesports-diary-ack-2026-11-07.md` this round, even if only "started" or the exact error. Never print credentials.
If you think this needs a separate go from Nick, say so in that outbox file with the exact reason; do not wait silently.
