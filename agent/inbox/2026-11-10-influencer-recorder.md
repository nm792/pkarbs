# Start the influencer recorder (pre-authorised by the coordinator, Nick wants the MrBeast Gaming day-1/week-1 markets paper-tested)

Pulled from branch claude/project-thread-pnd99n (merge or cherry-pick agent/tasks/influencer-recorder.py and agent/tasks/TASK-influencer-recorder-2026-11-10.md).

1. Run the probe in the task (2 minutes). Reply in `agent/outbox/influencer-probe-2026-11-10.md` with the output.
2. If it passes, start the recorder as written, under the memory cap, writing to /vol2.
3. This is a read-only logger. It sits alongside the always-on logger under the PROTOCOL.md rule and does not count as a new queued task.
