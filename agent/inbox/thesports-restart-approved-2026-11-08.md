# Nick APPROVED restarting the TheSports capture (written 2026-11-08T00:05Z)

Nick, 8 Nov 00:00:14Z, replying to the ask about the stopped recorder: **"Yes"**. This is his approval to relaunch.
Please (read-only for PM/TheSports, NO orders, delete nothing, no credentials in git):
1. Relaunch `live/thesports/capture.py` from the volume chunk dir, as in your `thesports-recorder-stopped-2026-11-07` note (same topics: csgo, dota2, tennis, basketball, lol; same books/markets/pmws). Respect the server charter (disk 15 GB free check) and keep a single instance.
2. In `agent/outbox/thesports-restart-2026-11-08.md` confirm RAN or NOT RAN, with: process start time, first new ts_mqtt and books timestamps after the restart, and row counts 10 minutes later.
3. Export and commit a slim for the 11:02Z-16:00Z gap (the data recorded after `slim-1102-32295`, until the 16:00:13Z stop) now, same layout as `slim-1102-32295`, parts under 5 MB. Then keep the 2 h export running.
Thanks. Assessment is waiting on this: reviews/thesports-trial-assessment.md.
