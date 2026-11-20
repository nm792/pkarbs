# IT 20 Nov 08:10Z: P91 result, box export routed

1. Goal: measure whether the live CS2 PandaScore feed leads Polymarket CS2 books enough to trade, using the protected pmcs2 recorder and the PandaScore capture.
2. Where it stands: both protected units were restarted at 07:45Z with floor 3 GB (pkarbs agent/status/pandascore.md, commit 4a2c3dd8). pmcs2 is active and its books file grew 306,988 bytes in 60 s. The PandaScore capture process (tmux pscap2) is up, but the agent saw no socket-open line and no new raw file (the local raw dir still holds only the 16 Nov file). No live CS2 match was on at the read.
3. Most important: the PandaScore capture output is unverified. If it does not write during the next live CS2 match, the in-round test gets no new matches.

Items
- P91 is closed (dialogue OPEN-DONE, 2f713f83). IT is not routing another PandaScore check yet (cost rule). NEEDS CHUNKING if you want one: give one read-only command, the time to run it (during a live CS2 match), and the line that proves the capture is writing (file path and expected log line).
- Your 07:50Z box export note (it/00-URGENT-PS-T0k-BOX-session-export-pandascore-hours.md) is the same ask as the paused P88z. IT reopened P88z as the first P row, pointing at your new note, steps 1 to 5, with the index written as ps_sample_index_box.json (dialogue 2f713f83). Root had 6.53 GB free at 07:21Z (dialogue status/T0k7.md), above its floor, so /tmp is fine for these small files.
- Shipping the idle folders (pkarbs/from-vol, pkarbs-ps-step2): T0k7 is already doing this in the background with no local copy (started 07:18:50Z, dialogue status/T0k7.md). T0k8 deletes the local folders only after rsync exit 0 and a clean checksum pass, from 08:20Z. VOL2 was 9.78 GB free at 08:00Z (IT 08:03Z, unsupported by a file here), so the margin comes back after T0k8. It is not added to P91.
- P queue order now: P88z, P86a (due 14:30Z), P86n, P90a, P92a, P87a, PSa, P84b2, P87b, P68a.
