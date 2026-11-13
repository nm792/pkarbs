# TO IT, URGENT: ruling needed on where the Goalserve payload store writes

Source: Hermes' measured status in agent/status/goalserve.md (15:17Z section).

- The esports changed-payload store is live (15:09:35Z, 279 MB/day gzipped, measured over 7.6 min).
- /vol2 is not a mounted volume on this box. It is a plain directory on root (/dev/sda1, 17.5 GB free, 55%).
  The real 98 GB data disk is at /mnt/HC_Volume_107257520 (69 GB free).
- So the payload store and the PandaScore capture both write to root, against charter clause 2.
- The store auto-stops at the 15 GB floor, but root carries every other writer.

Please rule today, before the LoL final on 14 Nov:
(a) point PAYDIR (and the PandaScore path) at the 98 GB disk and restart, or
(b) mount the 98 GB disk at /vol2, or
(c) accept root with the 15 GB auto-stop.

Do NOT stop the capture while ruling: the LoL final needs the payloads. Moving the path is fine,
losing the stream is not. Reply in agent/outbox. Nick approved the payload store itself at 14:43Z;
this is only about where it writes.
