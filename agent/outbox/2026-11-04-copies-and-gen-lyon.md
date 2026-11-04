# Reply: 2026-11-04-copies-and-gen-lyon (server agent)

Round timestamp 2026-11-04 02:36Z. All three items read-only — no code, restart or kill.

1. **CS2 hourly copy resumed + refreshed now.** rn1/scores/cs2/server-2026-11/ re-copied from /root/cs2logger/out/* to the live tail 02:36:26Z (was stale at 14:08Z). cs2_frames.jsonl.gz 1.79 MB, cs2_changes.jsonl.gz 0.66 MB, logger.log.gz; gzip -t OK. Logger PID 3497389 RUNNING, raw appending. Standing: refresh+commit the repo copy hourly while it runs.
2. **TES-IG committed.** The 3 Nov 20:30Z capture landed in the shared folder /mnt/project-files/rn1/scores/lol/live-2026-11/tesig/ (books 789 KB, frames 47 KB, polls 529 KB, capture.log). All four copied to rn1/scores/lol/live-2026-11/server-TES-IG/ in this repo. Frames only cover the start of game 1 (startingTime bug) as the item notes.
3. **GEN-LYON confirmed.** capture.js at agent/tasks/lol-live-capture/capture.js (mtime 2026-11-04T00:00Z) carries the PR#39 startingTime fix. window ~20:30Z tonight; output will be copied to rn1/scores/lol/live-2026-11/server-GEN-LYON/ every 10 min during the window and status updated.
