# Inbox: CS2 frame count after 02:10Z does not match the committed file

From: project thread (PK arbs), 3 Nov 2026 02:55Z
To: server agent (Hermes)

Thanks, the restart is confirmed from the raw copy (gap 02:09:58Z to 02:11:13Z, ~75 s).

One mismatch: your outbox says 7,647 lines with recv_iso >= 2026-11-03T02:10:00Z (46,257 total).
The committed rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz has 46,438 lines, and only 3,661 with
recv_iso >= 2026-11-03T02:10:00Z (newest 02:48:31.770Z).

Please say how you counted (command used), and recount on the committed file. No process change needed.
Reply in agent/outbox/2026-11-03-cs2-count-mismatch.md.
