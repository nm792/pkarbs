# To Hermes and IT, 13 Nov: APPROVED. Start the Goalserve esports capture NOW (APPROVALS item 13)

**Approval:** Nick wrote "yes" at 13:46Z on 13 Nov, in answer to this question from Claude: "Approve? Start capturing the Goalserve esports feed now, so it is running before the LoL final on 14 Nov." That yes is the human approval for item 13 as filed in `agent/status/goalserve-probe.md`. Please record it in APPROVALS.md item 13 as "approved by Nick, 13 Nov 13:46Z".

What to do:

1. Add `inplay-esports.gz` to the running Goalserve capture (`live/goalserve/capture.py`), same login/key query as the other four feeds, about 0.5 s polling as in `agent/tasks/TASK-goalserve-v2-2026-11-12.md`. Restart the `goalserve` tmux session if that is the only way. Keep the gap short and say how long it was.
2. Keep to charter clauses 5 and 15: log rows (recv_ns, sha1, bytes, changed, first_seen_ns), not full copies; no data on the root disk; write under /vol2 or the storage box. VOL2 is at about 94%, so check free space first and stop if it is below the floor.
3. Write the result to `agent/status/goalserve.md`: capture started yes/no, start time (UTC), and the gap.
4. One hour after the start, post the disk use for the esports log (MB for that hour and an MB/day estimate) in `agent/status/goalserve.md`.
5. Do not store the login or key anywhere in the repo.

Deadline: running before the LoL Worlds final on 14 Nov. Post status as soon as it is running, and again at the one-hour mark.
