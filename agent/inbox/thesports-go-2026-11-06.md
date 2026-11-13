# URGENT: GO from Nick for TASK-thesports-trial-2026-11-05 (written 2026-11-06T10:15Z)

Nick, 09:23Z 6 Nov, in the project thread: "Prime whitelisted and the agent has the access details." At 10:14Z he asked for the capture to be checked NOW. The task file on the default branch has said GO since PR #162 (09:51Z); your 09:38Z round held on an older line, and your 10:00Z round did not mention TheSports.

Do this now, in this round:
1. Confirm `/etc/pkarbs/thesports.env` exists with THESPORTS_USER and THESPORTS_SECRET (and THESPORTS_TOPICS from TheSports, if Nick gave them). Never print the values. If the file is missing, write `agent/status/thesports-trial.md` saying "credentials installed: no" and reply in `agent/outbox/2026-11-05-thesports-trial.md`; that is the only blocker.
2. If present, start Part B exactly as in the task file (12 h chunk, systemd-run scope, MemoryMax=500M, `--share` dir). Set `THESPORTS_TOPICS` to the topics TheSports issued; `#` will probably be refused.
3. Within 15 min of starting, commit `ts_mqtt.jsonl.gz` and `log.jsonl.gz` (even if tiny) to `rn1/scores/thesports/first/` on the default branch, and write `agent/status/thesports-trial.md` with: start time, credentials installed yes/no, the `mqtt_connect` rc, `mqtt_suback` rc values, and rows per sport topic. If `mqtt_connect` rc is 4 or 5 (bad user/secret or IP not authorised), or there is no LoL/Dota/cricket topic, say so in the first lines of the status file.
4. LoL first: Worlds semis are 7-8 Nov. Check the LoL topic delivers before anything else.
Report in `agent/outbox/2026-11-05-thesports-trial.md`. Same read-only rules as the task (no orders, no money).
