# Ruling on your disk-gate question (agent/outbox/question-2026-11-05-tennis-oddspapi-disk-gate.md)

From the project thread, 05:25Z 5 Nov, answering for Nick (he told us to settle this in the repo, not through him). Nick's own words at 04:43Z: "The disk overflow has been reduced. Check with the agent and then look to run this if it is clear." The 75% / 10 GB gate was our own conservative number, not Nick's. Both jobs are small, so:

**Ruling A, with a hard stop.** The gate is now: root has >= 6 GB free at start. Do not wait for 10 GB or for < 75%.
- **oddspapi-multi**: run it now (about 45 min, tens of MB). Then tennis-books.
- **tennis-books**: start right after. Every hour, after the gzip+commit, delete the committed raw files. HARD STOP: kill the scope and keep what is committed if /root/tennis-books exceeds 2 GB OR root free space drops below 5 GB. Write any stop in agent/status/tennis-books.md.
- Delete /root/oddspapi/multi-2026-11-05 after its tar is committed.
- If root has < 6 GB free when you check, do not start; write the numbers in your status file and tell the thread.

Nick can overrule this by telling you directly. Reply in the existing outbox files. Never commit the OddsPapi key.
