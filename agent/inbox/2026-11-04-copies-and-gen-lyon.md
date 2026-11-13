# Inbox: resume hourly copies; commit TES-IG capture; confirm GEN-LYON uses fixed capture.js

From: project thread (PK arbs), 4 Nov 2026 02:15Z
To: server agent (Hermes)

All three items are read-only copies or checks: no code change, restart or kill.

1. **CS2 hourly copy has stopped.** rn1/scores/cs2/server-2026-11/ was last refreshed 3 Nov 15:51Z (data to 14:08Z).
   Resume the hourly copy per agent/inbox/2026-11-03-cs2-logger-restart-proof.md step 3, and refresh it now.
2. **TES-IG server capture (3 Nov 20:30Z window).** Nothing from it is in the repo or the shared folder.
   Commit whatever it wrote (frames, polls, books, log; gzip if large) to rn1/scores/lol/live-2026-11/server-TES-IG/,
   even though the frames only cover the start of game 1 (startingTime bug).
3. **GEN-LYON tonight (4 Nov, window from ~20:30Z).** Confirm in agent/status/lol-live-capture.md that the capture
   will run with the capture.js from PR #39 (the startingTime fix), and copy its output to
   rn1/scores/lol/live-2026-11/server-GEN-LYON/ every 10 min during the window.

Reply in agent/outbox/2026-11-04-copies-and-gen-lyon.md.
