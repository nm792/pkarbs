# To Hermes, 13 Nov 05:05Z: two urgent items

Please do both now and post status in the repo (agent/status/), not in chat.

1. **TheSports export has stalled.** The last export is d3d521e64d at 22:37Z on 12 Nov. Check whether the 2-hourly export timer is alive, whether a push race (your 12 Nov P2 note) is blocking it, and whether VOL2 free space is below the 15 GB floor. Run one export by hand and confirm a newer ts_mqtt chunk lands on the default branch. The Dota test D1 is at 39 of 40 games and the TheSports trial ends 16 Nov.
2. **Goalserve probe.** Run `agent/inbox/2026-11-13-goalserve-retest-404s-with-exact-urls.md` and write `agent/status/goalserve-probe.md`. Esports first (LoL final 14 Nov). Redact secrets, never write the key to the repo.

Deadline for both status files: 06:00Z. Post status at the deadline even if unfinished.
